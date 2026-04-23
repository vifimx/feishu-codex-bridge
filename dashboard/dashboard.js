const LANGUAGE_KEY = "feishuCodexBridge.language";

const messages = {
  en: {
    documentTitle: "Feishu Codex Bridge",
    config: "config",
    skipToContent: "Skip to content",
    eyebrow: "Local Bridge",
    language: "Language",
    refreshAction: "Refresh",
    autoRefresh: "Auto",
    overview: "Overview",
    status: "Status",
    connection: "Connection",
    machine: "Machine",
    activeJobs: "Active Jobs",
    refreshTime: "Refresh",
    feishuConnection: "Feishu Connection",
    noConnectionState: "No connection state loaded.",
    startConnection: "Start Connection",
    stopConnection: "Stop Connection",
    windowsIntegration: "Windows Integration",
    noIntegrationState: "No integration state loaded.",
    startMenu: "Start Menu",
    startMenuHint: "Adds “Feishu Codex Bridge Dashboard” and “Feishu Codex Bridge Stop” to Windows search and All apps. Pinning to Start must be done manually from Windows.",
    addToStartMenu: "Add to Start Menu",
    remove: "Remove",
    dashboardAtSignIn: "Start Dashboard on Boot",
    connectionAtSignIn: "Start Connection on Boot",
    enable: "Enable",
    disable: "Disable",
    jobs: "Jobs",
    noJobsLoaded: "No jobs loaded.",
    cleanupJobs: "Clean History",
    cleaningJobs: "Cleaning job history...",
    cleanedJobs: "Cleaned {count} jobs.",
    configuration: "Configuration",
    sandbox: "Sandbox",
    timeoutSeconds: "Timeout Seconds",
    finalOutputIdle: "Final Output Idle",
    maxConcurrentJobs: "Max Concurrent Jobs",
    jobHistoryLimit: "Job History Limit",
    autoCleanupJobs: "Auto clean job history",
    deleteJobArtifacts: "Delete job artifacts",
    replyMaxChars: "Reply Max Chars",
    defaultModel: "Default Model",
    defaultReasoning: "Default Reasoning",
    fastModel: "Fast Model",
    fastReasoning: "Fast Reasoning",
    defaultTier: "Default Tier",
    fastTier: "Fast Tier",
    allowGroupCodex: "Allow group /ask",
    groupPlainText: "Group plain text as task",
    privatePlainText: "Private plain text as task",
    privatePollingFallback: "Private polling fallback",
    downloadIncomingMedia: "Download incoming media",
    acceptAny: "Accept @any",
    dispatchToPeers: "Dispatch to peers",
    matchPresetAliases: "Match preset task aliases",
    resolveContacts: "Resolve contacts",
    contactCacheTtl: "Contact Cache TTL",
    sessionsEnabled: "Continue conversations",
    queueWhileRunning: "Queue while running",
    editStatusMessage: "Edit status message",
    showDetailsByDefault: "Show details by default",
    showProgressByDefault: "Show progress by default",
    progressMaxLines: "Progress Lines",
    statusInterval: "Status Interval",
    commandOptions: "Command Options",
    skillOptions: "Skill Options",
    modelOptions: "Model Options JSON",
    accessDirectory: "Access Directory",
    addUser: "Add User",
    addUserGroup: "Add User Group",
    addGroup: "Add Group",
    users: "Users",
    userGroups: "User Groups",
    groups: "Groups",
    chatGroups: "Chats",
    searchAccess: "Search users, groups, chats",
    noAccessMatches: "No matching access targets.",
    accessTarget: "Access Target",
    userKey: "User Key",
    userGroupKey: "User Group Key",
    groupKey: "Group Key",
    label: "Label",
    openIds: "Open IDs",
    emails: "Emails",
    names: "Names / Aliases",
    chatIds: "Chat IDs",
    members: "Members",
    aliases: "Aliases",
    unrestricted: "Unrestricted",
    allowCodex: "Allow free-form tasks",
    showDetails: "Show Details",
    showProgress: "Show Progress",
    commands: "Commands",
    skills: "Skills",
    models: "Models",
    tasks: "Tasks",
    presetTasksJson: "Preset Tasks JSON",
    apply: "Apply",
    capabilities: "Capabilities",
    recentLogs: "Recent Logs",
    loading: "loading",
    unknown: "unknown",
    offline: "offline",
    ok: "ok",
    connected: "connected",
    stopped: "stopped",
    running: "running",
    queued: "queued",
    completed: "completed",
    failed: "failed",
    timedOut: "timed out",
    readOnly: "read only",
    writeEnabled: "write enabled",
    installed: "installed",
    partiallyInstalled: "partially installed",
    needsRepair: "needs repair",
    notInstalled: "not installed",
    enabled: "enabled",
    disabled: "disabled",
    available: "available",
    unsupported: "unsupported",
    controlDisabled: "control disabled",
    noPid: "no pid",
    pid: "pid {pid}",
    runtimeDashboardOnly: "dashboard-only",
    runtimeBridgeHosted: "bridge-hosted",
    runtimeUnknown: "unknown mode",
    connectionDetail: "{state} · {pid} · {mode}",
    integrationDetail: "{state} · {folder}",
    noRecordedJobs: "No recorded bridge jobs.",
    noJobsYet: "No jobs yet.",
    attachments: "attachments: {count}",
    noLogs: "No logs",
    codex: "Runner",
    lark: "Lark",
    workspaces: "Workspaces",
    modalities: "Modalities",
    maxJobs: "Max Jobs",
    routing: "Routing",
    access: "Access",
    presetTasks: "Preset Tasks",
    eventDelivery: "Event Delivery",
    stateDir: "State",
    logDir: "Logs",
    startingConnection: "Starting connection...",
    stoppingConnection: "Stopping connection...",
    connectionStarted: "Connection started · pid {pid}",
    connectionStopped: "Connection stopped · pid {pid}",
    connectionAlreadyRunning: "Connection is already running · pid {pid}",
    connectionNotRunning: "Connection is not running.",
    applying: "Applying...",
    updated: "Updated.",
    startMenuInstalled: "Installed “Feishu Codex Bridge Dashboard” and “Feishu Codex Bridge Stop”. Use Windows search or All apps; pinning to Start is manual.",
    startMenuRemoved: "Start Menu shortcuts removed.",
    dashboardStartupEnabled: "Dashboard boot startup enabled.",
    dashboardStartupDisabled: "Dashboard boot startup disabled.",
    connectionStartupEnabled: "Connection boot startup enabled.",
    connectionStartupDisabled: "Connection boot startup disabled.",
    noChanges: "No changes.",
    changed: "Changed: {keys}",
    restartRecommended: "restart recommended",
    error: "error",
    warn: "warn",
    debug: "debug",
    info: "info",
    raw: "raw",
  },
  "zh-CN": {
    documentTitle: "飞书 Codex 桥接",
    config: "配置",
    skipToContent: "跳到主要内容",
    eyebrow: "本地桥接",
    language: "语言",
    refreshAction: "刷新",
    autoRefresh: "自动",
    overview: "概览",
    status: "状态",
    connection: "连接",
    machine: "机器",
    activeJobs: "活动任务",
    refreshTime: "刷新时间",
    feishuConnection: "飞书连接",
    noConnectionState: "尚未加载连接状态。",
    startConnection: "启动连接",
    stopConnection: "关闭连接",
    windowsIntegration: "Windows 集成",
    noIntegrationState: "尚未加载集成状态。",
    startMenu: "开始菜单",
    startMenuHint: "会添加“Feishu Codex Bridge Dashboard”和“Feishu Codex Bridge Stop”，可在 Windows 搜索或“所有应用”中找到；固定到开始页需要在 Windows 中手动固定。",
    addToStartMenu: "添加到开始菜单",
    remove: "移除",
    dashboardAtSignIn: "开机启动面板",
    connectionAtSignIn: "开机启动连接",
    enable: "启用",
    disable: "禁用",
    jobs: "任务",
    noJobsLoaded: "尚未加载任务。",
    cleanupJobs: "清理历史",
    cleaningJobs: "正在清理任务历史...",
    cleanedJobs: "已清理 {count} 个任务。",
    configuration: "配置",
    sandbox: "沙箱",
    timeoutSeconds: "超时秒数",
    finalOutputIdle: "最终输出空闲秒数",
    maxConcurrentJobs: "最大并发任务",
    jobHistoryLimit: "任务历史保留数",
    autoCleanupJobs: "自动清理任务历史",
    deleteJobArtifacts: "同时删除任务产物",
    replyMaxChars: "回复最大字符数",
    defaultModel: "默认模型",
    defaultReasoning: "默认思考强度",
    fastModel: "快速模型",
    fastReasoning: "快速思考强度",
    defaultTier: "默认服务档位",
    fastTier: "快速服务档位",
    allowGroupCodex: "允许群聊 /ask",
    groupPlainText: "群聊普通文本作为任务",
    privatePlainText: "私聊普通文本作为任务",
    privatePollingFallback: "私聊轮询兜底",
    downloadIncomingMedia: "下载收到的媒体",
    acceptAny: "接受 @any",
    dispatchToPeers: "分发到 peer",
    matchPresetAliases: "匹配预设任务别名",
    resolveContacts: "解析通讯录",
    contactCacheTtl: "通讯录缓存秒数",
    sessionsEnabled: "连续会话",
    queueWhileRunning: "运行中自动排队",
    editStatusMessage: "编辑状态消息",
    showDetailsByDefault: "默认显示细节",
    showProgressByDefault: "默认显示进度",
    progressMaxLines: "进度行数",
    statusInterval: "状态更新间隔",
    commandOptions: "命令选项",
    skillOptions: "Skill 选项",
    modelOptions: "模型选项 JSON",
    accessDirectory: "访问目录",
    addUser: "新增用户",
    addUserGroup: "新增用户组",
    addGroup: "新增群聊",
    users: "用户",
    userGroups: "用户组",
    groups: "群聊",
    chatGroups: "群聊",
    searchAccess: "搜索用户、用户组、群聊",
    noAccessMatches: "没有匹配的访问目标。",
    accessTarget: "访问目标",
    userKey: "用户键",
    userGroupKey: "用户组键",
    groupKey: "群键",
    label: "名称",
    openIds: "Open IDs",
    emails: "邮箱",
    names: "名称 / 别名",
    chatIds: "Chat IDs",
    members: "成员",
    aliases: "别名",
    unrestricted: "无限制",
    allowCodex: "允许自由任务",
    showDetails: "显示细节",
    showProgress: "显示进度",
    commands: "命令",
    skills: "Skills",
    models: "模型",
    tasks: "任务",
    presetTasksJson: "预设任务 JSON",
    apply: "应用",
    capabilities: "能力",
    recentLogs: "最近日志",
    loading: "加载中",
    unknown: "未知",
    offline: "离线",
    ok: "正常",
    connected: "已连接",
    stopped: "已停止",
    running: "运行中",
    queued: "排队中",
    completed: "已完成",
    failed: "失败",
    timedOut: "已超时",
    readOnly: "只读",
    writeEnabled: "可写",
    installed: "已安装",
    partiallyInstalled: "部分添加",
    needsRepair: "需重新添加",
    notInstalled: "未安装",
    enabled: "已启用",
    disabled: "已禁用",
    available: "可用",
    unsupported: "不支持",
    controlDisabled: "控制已禁用",
    noPid: "无 pid",
    pid: "pid {pid}",
    runtimeDashboardOnly: "仅面板模式",
    runtimeBridgeHosted: "桥接托管模式",
    runtimeUnknown: "未知模式",
    connectionDetail: "{state} · {pid} · {mode}",
    integrationDetail: "{state} · {folder}",
    noRecordedJobs: "没有记录的桥接任务。",
    noJobsYet: "暂无任务。",
    attachments: "附件：{count}",
    noLogs: "暂无日志",
    codex: "执行器",
    lark: "Lark",
    workspaces: "工作区",
    modalities: "模态",
    maxJobs: "最大任务数",
    routing: "路由",
    access: "访问控制",
    presetTasks: "预设任务",
    eventDelivery: "事件接收",
    stateDir: "状态目录",
    logDir: "日志目录",
    startingConnection: "正在启动连接...",
    stoppingConnection: "正在关闭连接...",
    connectionStarted: "连接已启动 · pid {pid}",
    connectionStopped: "连接已关闭 · pid {pid}",
    connectionAlreadyRunning: "连接已在运行 · pid {pid}",
    connectionNotRunning: "连接未运行。",
    applying: "正在应用...",
    updated: "已更新。",
    startMenuInstalled: "已添加“Feishu Codex Bridge Dashboard”和“Feishu Codex Bridge Stop”。可在 Windows 搜索或“所有应用”中找到；固定到开始页需要手动固定。",
    startMenuRemoved: "开始菜单快捷方式已移除。",
    dashboardStartupEnabled: "已启用开机启动面板。",
    dashboardStartupDisabled: "已关闭开机启动面板。",
    connectionStartupEnabled: "已启用开机启动连接。",
    connectionStartupDisabled: "已关闭开机启动连接。",
    noChanges: "没有变更。",
    changed: "已变更：{keys}",
    restartRecommended: "建议重启",
    error: "错误",
    warn: "警告",
    debug: "调试",
    info: "信息",
    raw: "原始",
  },
};

const state = {
  refreshTimer: null,
  refreshMs: 5000,
  config: null,
  lang: initialLanguage(),
  lastStatus: null,
  lastJobs: null,
  lastLogs: null,
  lastConfigPayload: null,
  accessDraft: null,
  selectedAccessTarget: "",
  configEditing: false,
};

const $ = (selector) => document.querySelector(selector);

function initialLanguage() {
  const saved = localStorage.getItem(LANGUAGE_KEY);
  if (saved) return normalizeLanguage(saved);
  const languages = navigator.languages?.length ? navigator.languages : [navigator.language || "en"];
  return languages.some((language) => normalizeLanguage(language) === "zh-CN") ? "zh-CN" : "en";
}

function normalizeLanguage(language) {
  return String(language || "").toLowerCase().startsWith("zh") ? "zh-CN" : "en";
}

function locale() {
  return state.lang === "zh-CN" ? "zh-CN" : "en-US";
}

function t(key, values = {}) {
  const source = messages[state.lang]?.[key] ?? messages.en[key] ?? key;
  return source.replace(/\{(\w+)\}/g, (_, name) => (values[name] === undefined ? "" : String(values[name])));
}

function escapeHtml(value) {
  return text(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function text(value) {
  if (value === null || value === undefined || value === "") return "-";
  return String(value);
}

function compactJson(value, limit = 220) {
  const raw = typeof value === "string" ? value : JSON.stringify(value || {});
  return raw.length > limit ? `${raw.slice(0, limit).trim()}...` : raw;
}

function eventSummary(eventDelivery = {}) {
  const types = eventDelivery.event_types || [];
  const privateMode = eventDelivery.private_polling_fallback_enabled ? "polling fallback" : "event";
  return `${eventDelivery.transport || "-"} · ${types.length} events · private ${privateMode}`;
}

function accessSummary(access = {}) {
  return `identities=${access.identity_count || 0} · user_groups=${access.user_group_count || 0} · chats=${access.group_count || 0}`;
}

function formatTime(value = new Date()) {
  try {
    return new Intl.DateTimeFormat(locale(), {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }).format(value instanceof Date ? value : new Date(value));
  } catch {
    return text(value);
  }
}

function formatDateTime(value) {
  if (!value) return "-";
  try {
    return new Intl.DateTimeFormat(locale(), {
      dateStyle: "short",
      timeStyle: "medium",
    }).format(new Date(value));
  } catch {
    return text(value);
  }
}

function statusLabel(status) {
  const value = text(status).toLowerCase();
  const key = {
    ok: "ok",
    running: "running",
    queued: "queued",
    completed: "completed",
    failed: "failed",
    timed_out: "timedOut",
    stopped: "stopped",
    error: "error",
    warn: "warn",
    debug: "debug",
    info: "info",
    raw: "raw",
  }[value];
  return key ? t(key) : text(status);
}

function runtimeModeLabel(mode) {
  const key = {
    "dashboard-only": "runtimeDashboardOnly",
    "bridge-hosted": "runtimeBridgeHosted",
    unknown: "runtimeUnknown",
  }[mode || "unknown"];
  return key ? t(key) : text(mode);
}

function applyLanguage() {
  document.documentElement.lang = state.lang;
  document.title = t("documentTitle");
  $("#languageSelect").value = state.lang;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAriaLabel));
  });
}

function rerenderFromCache() {
  if (state.lastStatus) renderStatus(state.lastStatus);
  if (state.lastJobs) renderJobs(state.lastJobs);
  if (state.lastLogs) renderLogs(state.lastLogs);
  if (state.lastConfigPayload) renderConfig(state.lastConfigPayload);
}

function setLanguage(language, persist = true) {
  state.lang = normalizeLanguage(language);
  if (persist) localStorage.setItem(LANGUAGE_KEY, state.lang);
  applyLanguage();
  rerenderFromCache();
}

async function getJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

async function postJson(url, payload = {}) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.error || response.statusText);
  }
  return result;
}

function pill(status) {
  const value = text(status).toLowerCase();
  return `<span class="pill ${escapeHtml(value)}">${escapeHtml(statusLabel(status))}</span>`;
}

function setByName(name, value) {
  const field = document.querySelector(`[name="${name}"]`);
  if (!field) return;
  if (field.type === "checkbox") {
    field.checked = Boolean(value);
  } else if (field.dataset.json === "array") {
    field.value = Array.isArray(value)
      ? value.some((item) => typeof item === "object")
        ? JSON.stringify(value, null, 2)
        : value.join("\n")
      : "";
  } else if (field.dataset.json === "object") {
    field.value = value ? JSON.stringify(value, null, 2) : "{}";
  } else {
    field.value = value ?? "";
  }
}

function modelIdsFromConfig(config = state.config || {}) {
  const models = getByPath(config, "models.available") || [];
  return models
    .map((item) => (typeof item === "string" ? item : item?.id || item?.model || item?.name))
    .filter(Boolean);
}

function renderModelSelectOptions(config = state.config || {}) {
  const ids = modelIdsFromConfig(config);
  document.querySelectorAll("[data-model-select]").forEach((select) => {
    const current = select.value || getByPath(config, select.name) || "";
    select.innerHTML = [`<option value="">${escapeHtml(t("config"))}</option>`]
      .concat(ids.map((id) => `<option value="${escapeHtml(id)}">${escapeHtml(id)}</option>`))
      .join("");
    select.value = ids.includes(current) ? current : current || "";
    if (current && !ids.includes(current)) {
      select.insertAdjacentHTML("beforeend", `<option value="${escapeHtml(current)}">${escapeHtml(current)}</option>`);
      select.value = current;
    }
  });
}

function optionIds(kind) {
  if (kind === "commands") return (getByPath(state.config || {}, "commands.available") || state.lastStatus?.capabilities?.commands || []).map(String);
  if (kind === "skills") return (getByPath(state.config || {}, "skills.available") || state.lastStatus?.capabilities?.skills || []).map(String);
  if (kind === "models") return modelIdsFromConfig();
  if (kind === "tasks") return Object.keys(getByPath(state.config || {}, "preset_tasks") || {});
  return [];
}

function splitLines(value) {
  return String(value || "")
    .split(/\r?\n|,/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function listValue(value) {
  return Array.isArray(value) ? value.map(String) : [];
}

function choiceGroup(field, selected, options) {
  const values = new Set(listValue(selected));
  const allOptions = ["*"].concat(options.filter((item) => item !== "*"));
  return `
    <div class="choice-group" data-choice-field="${escapeHtml(field)}">
      ${allOptions
        .map(
          (item) => `
            <label class="chip-check">
              <input type="checkbox" value="${escapeHtml(item)}" ${values.has(item) ? "checked" : ""} />
              <span>${escapeHtml(item)}</span>
            </label>
          `,
        )
        .join("")}
    </div>
  `;
}

function accessPath(kind) {
  return {
    identity: "access.identities",
    user_group: "access.user_groups",
    group: "access.groups",
  }[kind];
}

function accessKindLabel(kind) {
  return {
    identity: t("users"),
    user_group: t("userGroups"),
    group: t("chatGroups"),
  }[kind] || kind;
}

function ensureAccessDraft() {
  if (state.accessDraft) return;
  state.accessDraft = {
    identity: JSON.parse(JSON.stringify(getByPath(state.config || {}, "access.identities") || {})),
    user_group: JSON.parse(JSON.stringify(getByPath(state.config || {}, "access.user_groups") || {})),
    group: JSON.parse(JSON.stringify(getByPath(state.config || {}, "access.groups") || {})),
  };
}

function accessTargets() {
  ensureAccessDraft();
  const targets = [];
  for (const kind of ["identity", "user_group", "group"]) {
    const collection = state.accessDraft[kind] || {};
    for (const [key, item] of Object.entries(collection)) {
      const haystack = [
        key,
        item.label,
        item.name,
        ...(item.aliases || []),
        ...(item.open_ids || []),
        ...(item.emails || []),
        ...(item.members || []),
        ...(item.chat_ids || []),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      targets.push({
        id: `${kind}:${key}`,
        kind,
        key,
        item,
        label: item.label || item.name || key,
        haystack,
      });
    }
  }
  return targets;
}

function defaultAccessItem(kind) {
  if (kind === "identity") {
    return { label: "", open_ids: [], emails: [], aliases: [], allow_codex: false, unrestricted: false, show_details: false, show_progress: false, commands: [], tasks: [], skills: [], models: [] };
  }
  return { label: "", enabled: true, members: [], allow_codex: false, unrestricted: false, show_details: false, show_progress: false, commands: [], tasks: [], skills: [], models: [] };
}

function selectedAccessTarget() {
  ensureAccessDraft();
  const targets = accessTargets();
  if (!targets.length) return null;
  let selected = targets.find((target) => target.id === state.selectedAccessTarget);
  if (!selected) {
    selected = targets[0];
    state.selectedAccessTarget = selected.id;
  }
  return selected;
}

function accessCard(kind, key, item = {}) {
  const isChatGroup = kind === "group";
  const isIdentity = kind === "identity";
  const fieldKey = isIdentity ? "userKey" : isChatGroup ? "groupKey" : "userGroupKey";
  const listLabel = isIdentity ? "openIds" : isChatGroup ? "chatIds" : "members";
  const listField = isIdentity ? "open_ids" : isChatGroup ? "chat_ids" : "members";
  return `
    <article class="access-card" data-access-kind="${escapeHtml(kind)}" data-original-key="${escapeHtml(key)}">
      <div class="access-card-head">
        <label>
          <span>${escapeHtml(t(fieldKey))}</span>
          <input data-access-field="key" value="${escapeHtml(key)}" />
        </label>
        <label>
          <span>${escapeHtml(t("label"))}</span>
          <input data-access-field="label" value="${escapeHtml(item.label || item.name || "")}" />
        </label>
      </div>
      <div class="access-card-grid">
        <label>
          <span>${escapeHtml(t(listLabel))}</span>
          <textarea data-access-list="${escapeHtml(listField)}" rows="3">${escapeHtml(listValue(item[listField]).join("\n"))}</textarea>
        </label>
        ${
          isIdentity
            ? `<label><span>${escapeHtml(t("emails"))}</span><textarea data-access-list="emails" rows="3">${escapeHtml(listValue(item.emails).join("\n"))}</textarea></label>`
            : `<label><span>${escapeHtml(t("aliases"))}</span><textarea data-access-list="aliases" rows="3">${escapeHtml(listValue(item.aliases).join("\n"))}</textarea></label>`
        }
        ${
          isIdentity
            ? `<label><span>${escapeHtml(t("names"))}</span><textarea data-access-list="aliases" rows="3">${escapeHtml(listValue(item.aliases).join("\n"))}</textarea></label>`
            : ""
        }
      </div>
      <div class="access-toggles">
        ${
          !isIdentity
            ? `<label class="check"><input data-access-bool="enabled" type="checkbox" ${item.enabled === false ? "" : "checked"} /><span>${escapeHtml(t("enabled"))}</span></label>`
            : ""
        }
        <label class="check"><input data-access-bool="allow_codex" type="checkbox" ${item.allow_codex ? "checked" : ""} /><span>${escapeHtml(t("allowCodex"))}</span></label>
        <label class="check"><input data-access-bool="unrestricted" type="checkbox" ${item.unrestricted ? "checked" : ""} /><span>${escapeHtml(t("unrestricted"))}</span></label>
        <label class="check"><input data-access-bool="show_details" type="checkbox" ${item.show_details ? "checked" : ""} /><span>${escapeHtml(t("showDetails"))}</span></label>
        <label class="check"><input data-access-bool="show_progress" type="checkbox" ${item.show_progress ? "checked" : ""} /><span>${escapeHtml(t("showProgress"))}</span></label>
      </div>
      <div class="access-permissions">
        <div><strong>${escapeHtml(t("commands"))}</strong>${choiceGroup("commands", item.commands, optionIds("commands"))}</div>
        <div><strong>${escapeHtml(t("tasks"))}</strong>${choiceGroup("tasks", item.tasks, optionIds("tasks"))}</div>
        <div><strong>${escapeHtml(t("skills"))}</strong>${choiceGroup("skills", item.skills, optionIds("skills"))}</div>
        <div><strong>${escapeHtml(t("models"))}</strong>${choiceGroup("models", item.models, optionIds("models"))}</div>
      </div>
    </article>
  `;
}

function renderAccessEditor() {
  const container = $("#accessEditor");
  if (!container) return;
  if (state.accessDraft) syncAccessDetail();
  ensureAccessDraft();
  const targets = accessTargets();
  const selected = selectedAccessTarget();
  let search = container.querySelector("#accessSearch")?.value || "";
  if (search === "-") search = "";
  const filtered = search
    ? targets.filter((target) => target.haystack.includes(search.trim().toLowerCase()))
    : targets;
  container.innerHTML = `
    <div class="access-layout">
      <aside class="access-sidebar">
        <label class="access-search">
          <span>${escapeHtml(t("searchAccess"))}</span>
          <input id="accessSearch" type="search" placeholder="${escapeHtml(t("searchAccess"))}" value="${escapeHtml(search)}" />
        </label>
        <div class="access-target-list">
          ${
            filtered.length
              ? filtered
                  .map(
                    (target) => `
                      <button type="button" class="access-target ${target.id === selected?.id ? "active" : ""}" data-access-target="${escapeHtml(target.id)}">
                        <span>${escapeHtml(accessKindLabel(target.kind))}</span>
                        <strong>${escapeHtml(target.label)}</strong>
                        <code>${escapeHtml(target.key)}</code>
                      </button>
                    `,
                  )
                  .join("")
              : `<p class="empty-copy">${escapeHtml(t("noAccessMatches"))}</p>`
          }
        </div>
      </aside>
      <div class="access-detail">
        ${
          selected
            ? `<h4>${escapeHtml(t("accessTarget"))}: ${escapeHtml(accessKindLabel(selected.kind))}</h4>${accessCard(selected.kind, selected.key, selected.item)}`
            : `<p class="empty-copy">${escapeHtml(t("noAccessMatches"))}</p>`
        }
      </div>
    </div>
  `;
  $("#accessSearch")?.addEventListener("input", renderAccessEditor);
  document.querySelectorAll("[data-access-target]").forEach((button) => {
    button.addEventListener("click", () => {
      syncAccessDetail();
      state.selectedAccessTarget = button.dataset.accessTarget;
      renderAccessEditor();
    });
  });
}

function syncAccessDetail() {
  ensureAccessDraft();
  const card = document.querySelector(".access-detail [data-access-kind]");
  if (!card) return;
  const kind = card.dataset.accessKind;
  const originalKey = card.dataset.originalKey;
  const key = card.querySelector('[data-access-field="key"]')?.value.trim();
  if (!kind || !originalKey || !key) return;
  const item = {};
  card.querySelectorAll("[data-access-field]").forEach((field) => {
    const name = field.dataset.accessField;
    if (name !== "key" && field.value.trim()) item[name] = field.value.trim();
  });
  card.querySelectorAll("[data-access-list]").forEach((field) => {
    item[field.dataset.accessList] = splitLines(field.value);
  });
  card.querySelectorAll("[data-access-bool]").forEach((field) => {
    item[field.dataset.accessBool] = Boolean(field.checked);
  });
  card.querySelectorAll("[data-choice-field]").forEach((group) => {
    item[group.dataset.choiceField] = Array.from(group.querySelectorAll("input:checked")).map((input) => input.value);
  });
  if (!state.accessDraft[kind]) state.accessDraft[kind] = {};
  if (originalKey !== key) {
    delete state.accessDraft[kind][originalKey];
  }
  state.accessDraft[kind][key] = item;
  state.selectedAccessTarget = `${kind}:${key}`;
}

function addAccessCard(kind) {
  ensureAccessDraft();
  syncAccessDetail();
  state.configEditing = true;
  const prefix = kind === "group" ? "chat" : kind === "user_group" ? "user-group" : "user";
  const key = `${prefix}-${Date.now()}`;
  if (!state.accessDraft[kind]) state.accessDraft[kind] = {};
  state.accessDraft[kind][key] = defaultAccessItem(kind);
  state.selectedAccessTarget = `${kind}:${key}`;
  renderAccessEditor();
}

function getByPath(object, path) {
  return path.split(".").reduce((current, part) => current && current[part], object);
}

function renderStatus(status) {
  state.lastStatus = status;
  const caps = status.capabilities || {};
  const connection = status.feishu_connection || {};
  const connectionRunning = Boolean(connection.running);

  $("#statusText").textContent = statusLabel(status.status || "unknown");
  $("#connectionText").textContent = connectionRunning ? t("connected") : t("stopped");
  $("#machineText").textContent = caps.machine_id || "-";
  $("#activeJobsText").textContent = String(status.active_jobs?.length || 0);
  $("#refreshText").textContent = formatTime();
  $("#connectionText").className = connectionRunning ? "ok-text" : "warn-text";

  const pid = connection.pid ? t("pid", { pid: connection.pid }) : t("noPid");
  const mode = connection.control_enabled === false ? t("controlDisabled") : runtimeModeLabel(status.runtime_mode);
  $("#connectionDetail").textContent = t("connectionDetail", {
    state: connectionRunning ? t("connected") : t("stopped"),
    pid,
    mode,
  });
  $("#startConnectionBtn").disabled = !connection.can_start;
  $("#stopConnectionBtn").disabled = !connection.can_stop;

  const config = status.dashboard || {};
  const nextRefreshMs = config.auto_refresh_sec ? Math.max(2, Number(config.auto_refresh_sec)) * 1000 : state.refreshMs;
  if (nextRefreshMs !== state.refreshMs) {
    state.refreshMs = nextRefreshMs;
    setAutoRefresh();
  }

  renderWindowsIntegration(status.windows_integration || {});

  const entries = [
    [t("codex"), caps.codex_cli],
    [t("lark"), caps.lark_cli],
    [t("workspaces"), (caps.workspaces || []).join(", ")],
    [t("modalities"), (caps.modalities || []).join(", ")],
    [t("maxJobs"), caps.max_concurrent_jobs],
    [t("routing"), compactJson(caps.routing)],
    [t("eventDelivery"), eventSummary(caps.event_delivery || {})],
    [t("access"), accessSummary(caps.access || {})],
    [t("presetTasks"), (caps.preset_tasks || []).map((task) => task.id).join(", ")],
    [t("stateDir"), status.state_dir],
    [t("logDir"), status.log_dir],
  ];
  $("#capabilities").innerHTML = entries
    .map(([key, value]) => `<div><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
    .join("");

  const counts = status.job_counts || {};
  const summary = Object.keys(counts).length
    ? Object.entries(counts)
        .map(([key, value]) => `${statusLabel(key)}: ${value}`)
        .join(" · ")
    : t("noRecordedJobs");
  $("#jobSummary").textContent = summary;
}

function setButton(id, enabled) {
  const button = $(id);
  if (button) button.disabled = !enabled;
}

function renderWindowsIntegration(integration) {
  const supported = Boolean(integration.supported);
  const controlEnabled = integration.control_enabled !== false;
  const startMenu = integration.start_menu || {};
  const startup = integration.startup || {};
  const dashboardStartup = startup.dashboard || {};
  const connectionStartup = startup.connection || {};

  $("#startMenuText").textContent = startMenu.installed
    ? t("installed")
    : startMenu.partial
      ? t("partiallyInstalled")
      : startMenu.needs_repair
        ? t("needsRepair")
        : t("notInstalled");
  $("#dashboardStartupText").textContent = dashboardStartup.installed ? t("enabled") : t("disabled");
  $("#connectionStartupText").textContent = connectionStartup.installed ? t("enabled") : t("disabled");

  const folder = startMenu.folder || "-";
  const integrationState = supported ? (controlEnabled ? t("available") : t("controlDisabled")) : t("unsupported");
  $("#windowsIntegrationDetail").textContent = t("integrationDetail", { state: integrationState, folder });

  const canChange = supported && controlEnabled;
  setButton("#installStartMenuBtn", canChange && !startMenu.installed);
  setButton("#removeStartMenuBtn", canChange && (startMenu.installed || startMenu.partial || startMenu.manifest_exists));
  setButton("#enableDashboardStartupBtn", canChange && !dashboardStartup.installed);
  setButton("#disableDashboardStartupBtn", canChange && dashboardStartup.installed);
  setButton("#enableConnectionStartupBtn", canChange && !connectionStartup.installed);
  setButton("#disableConnectionStartupBtn", canChange && connectionStartup.installed);
}

function renderJobs(jobs) {
  state.lastJobs = jobs;
  const container = $("#jobs");
  if (!jobs.length) {
    container.innerHTML = `<div class="empty-state"><p>${escapeHtml(t("noJobsYet"))}</p></div>`;
    return;
  }
  container.innerHTML = jobs
    .map((job) => {
      const link = job.codex_deeplink ? `<p><code translate="no">${escapeHtml(job.codex_deeplink)}</code></p>` : "";
      const error = job.error ? `<p>${escapeHtml(job.error)}</p>` : "";
      return `
        <article class="job">
          <header>
            <code translate="no">${escapeHtml(job.job_id)}</code>
            ${pill(job.status)}
          </header>
          <p>${escapeHtml(text(job.workspace))} · ${escapeHtml(formatDateTime(job.updated_at))}</p>
          <p>${escapeHtml(job.prompt_prefix)}</p>
          <p>${escapeHtml(t("attachments", { count: job.attachment_count || 0 }))}</p>
          ${link}
          ${error}
        </article>
      `;
    })
    .join("");
}

function renderLogs(logs) {
  state.lastLogs = logs;
  const container = $("#logs");
  if (!logs.length) {
    container.innerHTML = `<div class="log-line empty"><strong>${escapeHtml(t("noLogs"))}</strong></div>`;
    return;
  }
  container.innerHTML = logs
    .slice()
    .reverse()
    .map((item) => {
      const level = text(item.level).toLowerCase();
      const cls = level === "error" ? "failed" : level === "warn" ? "warn" : "ok";
      return `
        <div class="log-line">
          <code translate="no">${escapeHtml(formatDateTime(item.ts))}</code>
          <span class="pill ${escapeHtml(cls)}">${escapeHtml(statusLabel(level))}</span>
          <strong>${escapeHtml(item.message)}</strong>
        </div>
      `;
    })
    .join("");
}

function renderConfig(configPayload) {
  state.lastConfigPayload = configPayload;
  state.config = configPayload.config || {};
  state.accessDraft = null;
  renderModelSelectOptions(state.config);
  const writable = Boolean(configPayload.allow_config_write);
  const writeState = $("#configWriteState");
  writeState.textContent = writable ? t("writeEnabled") : t("readOnly");
  writeState.className = writable ? "pill ok" : "pill warn";
  document.querySelectorAll("#configForm button").forEach((button) => {
    button.disabled = !writable;
  });

  const fields = [
    "private.codex_sandbox",
    "private.codex_timeout_sec",
    "private.final_output_idle_grace_sec",
    "jobs.max_concurrent",
    "jobs.history_limit",
    "jobs.auto_cleanup_enabled",
    "jobs.cleanup_delete_artifacts",
    "reply.max_chars",
    "models.default.model",
    "models.default.reasoning_effort",
    "models.default.service_tier",
    "models.fast.model",
    "models.fast.reasoning_effort",
    "models.fast.service_tier",
    "public.allow_codex",
    "public.treat_all_text_as_codex",
    "private.treat_all_text_as_codex",
    "private.polling_fallback_enabled",
    "multimodal.download_incoming",
    "routing.accept_any_target",
    "routing.dispatch_to_peers",
    "access.enable_preset_intent_matching",
    "access.resolve_contacts_enabled",
    "access.contact_cache_ttl_sec",
    "sessions.enabled",
    "sessions.queue_while_running",
    "reply.edit_status_message",
    "reply.show_details_by_default",
    "reply.show_progress_by_default",
    "reply.progress_max_lines",
    "reply.status_update_interval_sec",
    "commands.available",
    "skills.available",
    "models.available",
    "preset_tasks",
  ];
  for (const field of fields) {
    setByName(field, getByPath(state.config, field));
  }
  renderAccessEditor();
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
    if (!state.configEditing) renderConfig(config);
    $("#statusText").className = "";
  } catch (error) {
    $("#statusText").textContent = t("offline");
    $("#configMessage").textContent = error.message;
  }
}

function connectionResultMessage(action, result) {
  if (result.status === "already_running") return t("connectionAlreadyRunning", { pid: result.pid || "-" });
  if (result.status === "not_running") return t("connectionNotRunning");
  if (action === "start") return t("connectionStarted", { pid: result.pid || "-" });
  if (action === "stop") return t("connectionStopped", { pid: result.pid || "-" });
  return result.message || t("updated");
}

async function controlConnection(action) {
  const message = $("#connectionMessage");
  const startButton = $("#startConnectionBtn");
  const stopButton = $("#stopConnectionBtn");
  startButton.disabled = true;
  stopButton.disabled = true;
  message.textContent = action === "start" ? t("startingConnection") : t("stoppingConnection");
  try {
    const result = await postJson(`/api/connection/${action}`);
    message.textContent = connectionResultMessage(action, result);
    await refreshAll();
  } catch (error) {
    message.textContent = error.message;
    await refreshAll();
  }
}

function windowsActionMessage(action) {
  const key = {
    "install-start-menu": "startMenuInstalled",
    "remove-start-menu": "startMenuRemoved",
    "enable-dashboard-startup": "dashboardStartupEnabled",
    "disable-dashboard-startup": "dashboardStartupDisabled",
    "enable-connection-startup": "connectionStartupEnabled",
    "disable-connection-startup": "connectionStartupDisabled",
  }[action];
  return key ? t(key) : t("updated");
}

async function controlWindowsIntegration(action) {
  const message = $("#windowsIntegrationMessage");
  const buttons = [
    "#installStartMenuBtn",
    "#removeStartMenuBtn",
    "#enableDashboardStartupBtn",
    "#disableDashboardStartupBtn",
    "#enableConnectionStartupBtn",
    "#disableConnectionStartupBtn",
  ];
  for (const id of buttons) setButton(id, false);
  message.textContent = t("applying");
  try {
    await postJson(`/api/windows-integration/${action}`);
    message.textContent = windowsActionMessage(action);
    await refreshAll();
  } catch (error) {
    message.textContent = error.message;
    await refreshAll();
  }
}

async function cleanupJobs() {
  const message = $("#jobsMessage");
  const button = $("#cleanupJobsBtn");
  const historyLimit = Number(getByPath(state.config || {}, "jobs.history_limit") || 50);
  if (button) button.disabled = true;
  message.textContent = t("cleaningJobs");
  try {
    const result = await postJson("/api/jobs/cleanup", { history_limit: historyLimit });
    message.textContent = t("cleanedJobs", { count: result.deleted_count || 0 });
    await refreshAll();
  } catch (error) {
    message.textContent = error.message;
  } finally {
    if (button) button.disabled = false;
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
      const raw = element.value.trim();
      value = raw.startsWith("[")
        ? JSON.parse(raw || "[]")
        : raw
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
  syncAccessDetail();
  ensureAccessDraft();
  const identities = state.accessDraft.identity || {};
  const userGroups = state.accessDraft.user_group || {};
  const groups = state.accessDraft.group || {};
  if (JSON.stringify(identities) !== JSON.stringify(getByPath(state.config || {}, "access.identities") || {})) {
    updates["access.identities"] = identities;
  }
  if (JSON.stringify(userGroups) !== JSON.stringify(getByPath(state.config || {}, "access.user_groups") || {})) {
    updates["access.user_groups"] = userGroups;
  }
  if (JSON.stringify(groups) !== JSON.stringify(getByPath(state.config || {}, "access.groups") || {})) {
    updates["access.groups"] = groups;
  }
  return updates;
}

async function applyConfig(event) {
  event.preventDefault();
  const message = $("#configMessage");
  const updates = collectUpdates();
  if (!Object.keys(updates).length) {
    message.textContent = t("noChanges");
    state.configEditing = false;
    return;
  }
  try {
    const result = await postJson("/api/config", { updates });
    const restart = result.restart_recommended ? ` · ${t("restartRecommended")}` : "";
    message.textContent = `${t("changed", { keys: result.changed.join(", ") })}${restart}`;
    state.configEditing = false;
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

$("#languageSelect").addEventListener("change", (event) => setLanguage(event.target.value));
$("#refreshBtn").addEventListener("click", refreshAll);
$("#cleanupJobsBtn").addEventListener("click", cleanupJobs);
$("#startConnectionBtn").addEventListener("click", () => controlConnection("start"));
$("#stopConnectionBtn").addEventListener("click", () => controlConnection("stop"));
$("#installStartMenuBtn").addEventListener("click", () => controlWindowsIntegration("install-start-menu"));
$("#removeStartMenuBtn").addEventListener("click", () => controlWindowsIntegration("remove-start-menu"));
$("#enableDashboardStartupBtn").addEventListener("click", () => controlWindowsIntegration("enable-dashboard-startup"));
$("#disableDashboardStartupBtn").addEventListener("click", () => controlWindowsIntegration("disable-dashboard-startup"));
$("#enableConnectionStartupBtn").addEventListener("click", () => controlWindowsIntegration("enable-connection-startup"));
$("#disableConnectionStartupBtn").addEventListener("click", () => controlWindowsIntegration("disable-connection-startup"));
$("#addIdentityBtn").addEventListener("click", () => addAccessCard("identity"));
$("#addUserGroupBtn").addEventListener("click", () => addAccessCard("user_group"));
$("#addGroupBtn").addEventListener("click", () => addAccessCard("group"));
$("#autoRefresh").addEventListener("change", setAutoRefresh);
$("#configForm").addEventListener("submit", applyConfig);
$("#configForm").addEventListener("input", () => {
  state.configEditing = true;
});
$("#configForm").addEventListener("change", () => {
  state.configEditing = true;
});

applyLanguage();
refreshAll().then(setAutoRefresh);
