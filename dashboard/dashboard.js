const state = {
  refreshTimer: null,
  refreshMs: 5000,
  config: null,
};

const $ = (selector) => document.querySelector(selector);

async function getJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

function text(value) {
  if (value === null || value === undefined || value === "") return "-";
  return String(value);
}

function pill(status) {
  const value = text(status).toLowerCase();
  return `<span class="pill ${value}">${text(status)}</span>`;
}

function setByName(name, value) {
  const field = document.querySelector(`[name="${name}"]`);
  if (!field) return;
  if (field.type === "checkbox") {
    field.checked = Boolean(value);
  } else if (field.dataset.json === "array") {
    field.value = Array.isArray(value) ? value.join("\n") : "";
  } else if (field.dataset.json === "object") {
    field.value = value ? JSON.stringify(value, null, 2) : "{}";
  } else {
    field.value = value ?? "";
  }
}

function getByPath(object, path) {
  return path.split(".").reduce((current, part) => current && current[part], object);
}

function renderStatus(status) {
  const caps = status.capabilities || {};
  $("#statusText").textContent = status.status || "unknown";
  $("#machineText").textContent = caps.machine_id || "-";
  $("#activeJobsText").textContent = String(status.active_jobs?.length || 0);
  $("#refreshText").textContent = new Date().toLocaleTimeString();

  const config = status.dashboard || {};
  if (config.auto_refresh_sec) {
    state.refreshMs = Math.max(2, Number(config.auto_refresh_sec)) * 1000;
  }

  const entries = [
    ["Codex", caps.codex_cli],
    ["Lark", caps.lark_cli],
    ["Workspaces", (caps.workspaces || []).join(", ")],
    ["Modalities", (caps.modalities || []).join(", ")],
    ["Max Jobs", caps.max_concurrent_jobs],
    ["Routing", JSON.stringify(caps.routing || {})],
    ["Access", JSON.stringify(caps.access || {})],
    ["Preset Tasks", (caps.preset_tasks || []).map((task) => task.id).join(", ")],
    ["State", status.state_dir],
    ["Logs", status.log_dir],
  ];
  $("#capabilities").innerHTML = entries
    .map(([key, value]) => `<div><span>${key}</span><strong>${text(value)}</strong></div>`)
    .join("");

  const counts = status.job_counts || {};
  const summary = Object.keys(counts).length
    ? Object.entries(counts).map(([key, value]) => `${key}: ${value}`).join(" · ")
    : "No recorded bridge jobs.";
  $("#jobSummary").textContent = summary;
}

function renderJobs(jobs) {
  const container = $("#jobs");
  if (!jobs.length) {
    container.innerHTML = `<div class="job"><p>No jobs yet.</p></div>`;
    return;
  }
  container.innerHTML = jobs
    .map((job) => {
      const link = job.codex_deeplink ? `<p><code>${job.codex_deeplink}</code></p>` : "";
      const error = job.error ? `<p>${job.error}</p>` : "";
      return `
        <article class="job">
          <header>
            <code>${job.job_id}</code>
            ${pill(job.status)}
          </header>
          <p>${text(job.workspace)} · ${text(job.updated_at)}</p>
          <p>${text(job.prompt_prefix)}</p>
          <p>attachments=${job.attachment_count || 0}</p>
          ${link}
          ${error}
        </article>
      `;
    })
    .join("");
}

function renderLogs(logs) {
  const container = $("#logs");
  if (!logs.length) {
    container.innerHTML = `<div class="log-line"><strong>No logs</strong></div>`;
    return;
  }
  container.innerHTML = logs
    .slice()
    .reverse()
    .map((item) => {
      const level = text(item.level);
      const cls = level === "error" ? "failed" : level === "warn" ? "warn" : "ok";
      return `
        <div class="log-line">
          <code>${text(item.ts)}</code>
          <span class="pill ${cls}">${level}</span>
          <strong>${text(item.message)}</strong>
        </div>
      `;
    })
    .join("");
}

function renderConfig(configPayload) {
  state.config = configPayload.config || {};
  const writable = Boolean(configPayload.allow_config_write);
  const writeState = $("#configWriteState");
  writeState.textContent = writable ? "write enabled" : "read only";
  writeState.className = writable ? "pill ok" : "pill warn";
  $("#configForm button").disabled = !writable;

  const fields = [
    "private.codex_sandbox",
    "private.codex_timeout_sec",
    "jobs.max_concurrent",
    "reply.max_chars",
    "access.trusted_sender_open_ids",
    "access.limited_sender_open_ids",
    "access.limited_allowed_commands",
    "access.limited_allowed_task_ids",
    "public.allow_codex",
    "public.treat_all_text_as_codex",
    "private.treat_all_text_as_codex",
    "multimodal.download_incoming",
    "routing.accept_any_target",
    "routing.dispatch_to_peers",
    "access.enable_preset_intent_matching",
    "preset_tasks",
  ];
  for (const field of fields) {
    setByName(field, getByPath(state.config, field));
  }
}

async function refreshAll() {
  try {
    const [status, jobs, logs, config] = await Promise.all([
      getJson("/api/status"),
      getJson("/api/jobs?limit=30"),
      getJson("/api/logs?limit=80"),
      getJson("/api/config"),
    ]);
    renderStatus(status);
    renderJobs(jobs);
    renderLogs(logs);
    renderConfig(config);
    $("#statusText").className = "";
  } catch (error) {
    $("#statusText").textContent = "offline";
    $("#configMessage").textContent = error.message;
  }
}

function collectUpdates() {
  const updates = {};
  const form = $("#configForm");
  for (const element of form.elements) {
    if (!element.name) continue;
    const oldValue = getByPath(state.config || {}, element.name);
    let value;
    if (element.type === "checkbox") {
      value = element.checked;
    } else if (element.type === "number") {
      value = Number(element.value);
    } else if (element.dataset.json === "array") {
      value = element.value
        .split(/\r?\n|,/)
        .map((item) => item.trim())
        .filter(Boolean);
    } else if (element.dataset.json === "object") {
      value = JSON.parse(element.value || "{}");
    } else {
      value = element.value;
    }
    if (JSON.stringify(value) !== JSON.stringify(oldValue)) {
      updates[element.name] = value;
    }
  }
  return updates;
}

async function applyConfig(event) {
  event.preventDefault();
  const message = $("#configMessage");
  const updates = collectUpdates();
  if (!Object.keys(updates).length) {
    message.textContent = "No changes.";
    return;
  }
  try {
    const response = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify({ updates }),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || response.statusText);
    }
    message.textContent = `Changed: ${result.changed.join(", ")}${result.restart_recommended ? " · restart recommended" : ""}`;
    await refreshAll();
  } catch (error) {
    message.textContent = error.message;
  }
}

function setAutoRefresh() {
  if (state.refreshTimer) {
    clearInterval(state.refreshTimer);
    state.refreshTimer = null;
  }
  if ($("#autoRefresh").checked) {
    state.refreshTimer = setInterval(refreshAll, state.refreshMs);
  }
}

$("#refreshBtn").addEventListener("click", refreshAll);
$("#autoRefresh").addEventListener("change", setAutoRefresh);
$("#configForm").addEventListener("submit", applyConfig);

refreshAll().then(setAutoRefresh);
