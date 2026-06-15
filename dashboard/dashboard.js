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
    restartDashboard: "Restart Dashboard",
    restartAll: "Restart All",
    windowsIntegration: "Windows Integration",
    noIntegrationState: "No integration state loaded.",
    startMenu: "Start Menu",
    startMenuHint: "Adds “Feishu Codex Bridge Dashboard” and “Feishu Codex Bridge Stop” to Windows search and All apps. Pinning to Start must be done manually from Windows.",
    addToStartMenu: "Add to Start Menu",
    remove: "Remove",
    dashboardAtSignIn: "Start Dashboard at Sign-in",
    connectionAtSignIn: "Start Connection at Sign-in",
    enable: "Enable",
    enableAsAdmin: "Enable as Admin",
    disable: "Disable",
    jobs: "Jobs",
    noJobsLoaded: "No jobs loaded.",
    cleanupJobs: "Clean History",
    cleaningJobs: "Cleaning job history...",
    cleanedJobs: "Cleaned {count} jobs.",
    configuration: "Configuration",
    configurationTargets: "Configuration Targets",
    globalAndDefaults: "Default Configuration",
    defaultConfig: "Default Configuration",
    globalDefaults: "Runtime Defaults",
    searchConfigTargets: "Search defaults, users, user groups, chats",
    assistantPrivacyGroup: "Assistant & Privacy",
    assistantPrivacyHint: "Identity, public answer style, and hidden internals.",
    modelGroup: "Models",
    modelGroupHint: "Default and fast profiles used by incoming jobs.",
    runtimeGroup: "Runtime & Jobs",
    runtimeGroupHint: "Codex path, sandbox, timeouts, concurrency, and history retention.",
    conversationReplyGroup: "Conversation & Replies",
    conversationReplyHint: "Topic mode, status cards, debug details, and progress summaries.",
    responseTargetGroup: "Response Targets",
    responseTargetHint: "Controls whether this bridge accepts @any jobs and whether chat messages must mention the bot.",
    routingGroup: "Routing & Intake",
    routingGroupHint: "Which messages become executable tasks, media handling, peer routing, and contact matching.",
    detectedRuntimeGroup: "Detected Options",
    detectedRuntimeHint: "Read-only skills and models discovered from the local runtime.",
    sandbox: "Sandbox",
    defaultWorkspace: "Default Workspace",
    codexHomeDir: "Codex Config Directory",
    timeoutSeconds: "Timeout Seconds",
    activeOutputGrace: "Active Output Grace",
    timeoutExtension: "Timeout Extension",
    finalOutputReady: "Final Output Ready",
    finalOutputIdle: "Final Output Idle",
    maxConcurrentJobs: "Max Concurrent Jobs",
    jobHistoryLimit: "Job History Limit",
    autoCleanupJobs: "Auto clean job history",
    deleteJobArtifacts: "Delete job artifacts",
    replyMaxChars: "Reply Max Chars",
    assistantDisplayName: "Assistant Name",
    assistantIdentityPrompt: "Assistant Identity Prompt",
    hideInternalIdentity: "Hide internal identity",
    defaultModel: "Default Model",
    defaultReasoning: "Default Reasoning",
    fastModel: "Fast Model",
    fastReasoning: "Fast Reasoning",
    defaultTier: "Normal Task Tier",
    fastTier: "mode=fast Tier",
    allowGroupCodex: "Allow group /ask",
    groupPlainText: "Group plain text as task",
    privatePlainText: "Private plain text as task",
    privatePollingFallback: "Private polling fallback",
    downloadIncomingMedia: "Download incoming media",
    acceptAny: "Accept @any",
    onlyRespondToBot: "Group: only respond to @bot",
    privateOnlyRespondToBot: "Private: only respond to @bot",
    dispatchToPeers: "Peer forwarding",
    dispatchToPeersHint: "Only useful for multi-node bridge deployments with peers.nodes configured. With no peers, it has no effect.",
    matchPresetAliases: "Auto-match executable tasks",
    resolveContacts: "Contact-assisted user matching",
    resolveContactsHint: "Uses Feishu contact profiles to match configured names, emails, mobiles, and aliases. Open ID matching still works without this.",
    contactCacheTtl: "Contact Cache TTL",
    sessionsEnabled: "Continue conversations",
    sessionMode: "Conversation Mode",
    sessionModeContinuous: "Continuous",
    sessionModeTopic: "Topic",
    topicReplyInThread: "Use Feishu thread topics",
    queueWhileRunning: "Queue while running",
    editStatusMessage: "Edit status message",
    showDetailsByDefault: "Show details by default",
    showProgressByDefault: "Show progress by default",
    progressMaxLines: "Progress Lines",
    statusInterval: "Status Interval",
    detectedRuntimeSkills: "Detected runtime skills",
    detectedRuntimeModels: "Detected runtime models",
    noneDetected: "None detected",
    accessDirectory: "Access Directory",
    defaultPolicy: "Default Template",
    defaultTemplate: "New user/group template",
    permissionTemplates: "Permission Templates",
    permissionDefaults: "Access baseline",
    permissionPreset: "Template",
    presetCustom: "Custom",
    identityPresetOption: "{label}",
    identityPresetNote: "Templates define reusable full access configurations.",
    syncedPermissionPreset: "Follows template",
    templateOnly: "Template",
    templateOnlyHint: "Templates are reusable configurations and do not apply by membership.",
    settingsOverrides: "Configuration",
    settingsOverridesHint: "Blank runtime fields use the global runtime defaults.",
    inheritDefault: "Inherit default",
    assistantOverrides: "Assistant identity",
    modelOverrides: "Model defaults",
    runtimeOverrides: "Runtime defaults",
    replyOverrides: "Reply visibility",
    addUser: "Add User",
    addUserGroup: "Add Template",
    addGroup: "Add Group",
    discoverAccess: "Discover Chats",
    discoveringAccess: "Discovering bot chats and members...",
    discoveredAccess: "Discovered {chats} chats and {users} users. Added {newChats} chats, {newUsers} users, and updated {updated} existing entries in the draft with the default template.",
    deleteAccessTarget: "Delete Target",
    users: "Users",
    userGroups: "Templates",
    groups: "Groups",
    chatGroups: "Chats",
    searchAccess: "Search users, groups, chats",
    noAccessMatches: "No matching access targets.",
    accessTarget: "Access Target",
    userKey: "User Key",
    userGroupKey: "Template Key",
    groupKey: "Group Key",
    label: "Display Label",
    openIds: "Match Open IDs",
    emails: "Match Emails",
    names: "Match Names",
    chatIds: "Chat IDs",
    members: "Member Keys / IDs",
    aliases: "Match Aliases",
    searchAliases: "Search Aliases",
    unrestricted: "Admin unrestricted",
    allowCodex: "Allow free-form /ask",
    accessModeHint: "Select approved main tasks here. Free-form task and Admin unrestricted are virtual tasks for open-ended natural-language use.",
    taskPermissionHint: "Allowed manual and automatic parent tasks for this target. Subtask overrides below can narrow them.",
    freeTaskLimitHint: "Only applies to free-form /ask requests. Executable tasks bring their configured required skills with the task.",
    freeFormTask: "Free-form task",
    unrestrictedTask: "Admin unrestricted",
    showDetails: "Show Details",
    showProgress: "Show Progress",
    skills: "Free-form Skills",
    models: "Free-form Models",
    tasks: "Executable tasks",
    presetTasksJson: "Executable Tasks JSON",
    executableTasks: "Executable Tasks",
    addExecutableTask: "Add Task",
    deleteExecutableTask: "Delete Task",
    taskKey: "Task Key",
    taskDescription: "Description",
    taskAliases: "Aliases",
    taskWorkspace: "Workspace",
    taskRequiredSkills: "Required Skills",
    taskAllowedChats: "Allowed Chat IDs",
    taskAllowedSenders: "Allowed Sender Open IDs",
    taskOutputExpectations: "Output Expectations",
    taskPromptTemplate: "Prompt Template",
    noExecutableTasks: "No executable tasks configured.",
    taskOverview: "Task Overview",
    taskSubtasks: "Response Subtasks",
    taskExecution: "Execution Scope",
    taskBackground: "Background",
    addSubtask: "Add Subtask",
    deleteSubtask: "Delete",
    subtaskId: "Subtask ID",
    subtaskLabel: "Label",
    subtaskType: "Type",
    subtaskManual: "Manual",
    subtaskAutomatic: "Automatic",
    subtaskAliases: "Aliases",
    subtaskDescription: "Description",
    subtaskPrompt: "Instructions",
    subtaskSchedule: "Schedule",
    subtaskAction: "Automatic Action",
    automaticInput: "Automatic run instructions",
    subtaskOverrides: "Subtask Overrides",
    manualSubtaskOverride: "Manual allowed subtasks",
    autoSubtaskOverride: "Auto-trigger subtasks",
    restrictToChecked: "Restrict to checked",
    scheduledTasks: "Task Scheduler",
    scheduledTasksHint: "Automatic sub-tasks are configured inside executable tasks. A chat or policy must explicitly allow them through automatic sub-task overrides.",
    scheduleGlobalEnabled: "Enable automatic sub-tasks",
    scheduleTimezone: "Scheduler timezone",
    schedulePollInterval: "Poll interval",
    addScheduledTask: "Add Auto Task",
    deleteScheduledTask: "Delete Auto Task",
    noScheduledTasks: "No automatic tasks configured.",
    scheduleId: "Auto Task ID",
    scheduleKind: "Action",
    scheduleKindMessage: "Send message",
    scheduleKindPresetTask: "Run executable task",
    scheduleTaskId: "Executable task",
    scheduleWeekdays: "Weekdays",
    scheduleTime: "Time",
    scheduleNoTime: "Not set",
    scheduleCatchup: "Catch-up minutes",
    minutes: "{count} min",
    scheduleChatIds: "Target Chat IDs",
    scheduleMessage: "Message",
    scheduleInput: "Task Input",
    suppressNoopReply: "Suppress no-op reply",
    scheduleTrigger: "Trigger",
    scheduleTarget: "Target",
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
    roundCompleted: "round complete",
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
    integrationDetail: "{state} · current-user sign-in · {folder}",
    integrationDetailNoFolder: "{state} · current-user sign-in",
    startupTaskHint: "Scheduled Task: {task}",
    startupAdminTaskHint: "Administrator Scheduled Task: {task}",
    startupShortcutHint: "Startup folder shortcut: {path}",
    noRecordedJobs: "No recorded bridge jobs.",
    noJobsYet: "No jobs yet.",
    viewDetails: "View Details",
    closeDetails: "Close",
    loadingJobDetails: "Loading job details...",
    jobDetails: "Job Details",
    jobMetadata: "Metadata",
    jobFiles: "Files",
    inputAttachments: "Input Attachments",
    jobTimeline: "Timeline",
    rawJobRecord: "Raw Job Record",
    openFile: "Open File",
    missingFile: "Missing file",
    noPreview: "No inline preview for this file type.",
    noAttachments: "No downloaded attachments.",
    noEvents: "No recorded timeline events.",
    previewTruncated: "Preview truncated.",
    bytes: "{count} bytes",
    attachments: "attachments: {count}",
    noLogs: "No logs",
    codex: "Runner",
    codexHome: "Codex Home",
    lark: "Lark",
    workspaces: "Workspaces",
    modalities: "Modalities",
    maxJobs: "Max Jobs",
    routing: "Routing",
    access: "Access",
    presetTasks: "Executable Tasks",
    eventDelivery: "Event Delivery",
    stateDir: "State",
    logDir: "Logs",
    startingConnection: "Starting connection...",
    stoppingConnection: "Stopping connection...",
    restartingDashboard: "Restarting dashboard...",
    restartingAll: "Restarting dashboard and connection...",
    connectionStarted: "Connection started · pid {pid}",
    connectionStopped: "Connection stopped · pid {pid}",
    connectionAlreadyRunning: "Connection is already running · pid {pid}",
    connectionNotRunning: "Connection is not running.",
    dashboardRestarting: "Dashboard is restarting. This page will reconnect shortly.",
    allRestarting: "Dashboard and connection are restarting. This page will reconnect shortly.",
    applying: "Applying...",
    updated: "Updated.",
    startMenuInstalled: "Installed “Feishu Codex Bridge Dashboard” and “Feishu Codex Bridge Stop”. Use Windows search or All apps; pinning to Start is manual.",
    startMenuRemoved: "Start Menu shortcuts removed.",
    dashboardStartupEnabled: "Dashboard sign-in startup enabled.",
    dashboardStartupAdminEnabled: "Dashboard sign-in startup enabled with administrator privileges.",
    dashboardStartupDisabled: "Dashboard sign-in startup disabled.",
    connectionStartupEnabled: "Connection sign-in startup enabled.",
    connectionStartupAdminEnabled: "Connection sign-in startup enabled with administrator privileges.",
    connectionStartupDisabled: "Connection sign-in startup disabled.",
    applyingAdmin: "Waiting for administrator confirmation...",
    noChanges: "No changes.",
    changed: "Changed: {keys}",
    skippedReadonly: "Skipped read-only fields: {keys}",
    unsavedConfig: "Unsaved changes. Apply to persist them.",
    restartRecommended: "restart recommended",
    connectionRestartRecommended: "connection restart recommended",
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
    restartDashboard: "重启面板",
    restartAll: "全部重启",
    windowsIntegration: "Windows 集成",
    noIntegrationState: "尚未加载集成状态。",
    startMenu: "开始菜单",
    startMenuHint: "会添加“Feishu Codex Bridge Dashboard”和“Feishu Codex Bridge Stop”，可在 Windows 搜索或“所有应用”中找到；固定到开始页需要在 Windows 中手动固定。",
    addToStartMenu: "添加到开始菜单",
    remove: "移除",
    dashboardAtSignIn: "登录时启动面板",
    connectionAtSignIn: "登录时启动连接",
    enable: "启用",
    enableAsAdmin: "以管理员启用",
    disable: "禁用",
    jobs: "任务",
    noJobsLoaded: "尚未加载任务。",
    cleanupJobs: "清理历史",
    cleaningJobs: "正在清理任务历史...",
    cleanedJobs: "已清理 {count} 个任务。",
    configuration: "配置",
    configurationTargets: "配置对象",
    globalAndDefaults: "默认配置",
    defaultConfig: "默认配置",
    globalDefaults: "运行默认",
    searchConfigTargets: "搜索默认配置、用户、用户组、群聊",
    assistantPrivacyGroup: "助手与隐私",
    assistantPrivacyHint: "身份、对外回答风格和内部信息隐藏。",
    modelGroup: "模型",
    modelGroupHint: "新任务使用的默认和快速模型配置。",
    runtimeGroup: "运行与任务",
    runtimeGroupHint: "Codex 路径、沙箱、超时、并发和历史保留。",
    conversationReplyGroup: "会话与回复",
    conversationReplyHint: "话题模式、状态卡片、调试细节和进度摘要。",
    responseTargetGroup: "响应目标",
    responseTargetHint: "控制是否接受 @any 任务，以及聊天消息是否必须 @机器人。",
    routingGroup: "路由与接收",
    routingGroupHint: "哪些消息进入可执行任务、媒体处理、Peer 路由和通讯录匹配。",
    detectedRuntimeGroup: "已识别选项",
    detectedRuntimeHint: "从本地运行时识别到的 Skills 和模型，只读展示。",
    sandbox: "沙箱",
    defaultWorkspace: "默认工作区",
    codexHomeDir: "Codex 配置目录",
    timeoutSeconds: "超时秒数",
    activeOutputGrace: "活跃输出宽限秒数",
    timeoutExtension: "超时延长上限秒数",
    finalOutputReady: "最终输出就绪秒数",
    finalOutputIdle: "最终输出空闲秒数",
    maxConcurrentJobs: "最大并发任务",
    jobHistoryLimit: "任务历史保留数",
    autoCleanupJobs: "自动清理任务历史",
    deleteJobArtifacts: "同时删除任务产物",
    replyMaxChars: "回复最大字符数",
    assistantDisplayName: "助手名称",
    assistantIdentityPrompt: "助手身份提示",
    hideInternalIdentity: "隐藏内部身份",
    defaultModel: "默认模型",
    defaultReasoning: "默认思考强度",
    fastModel: "快速模型",
    fastReasoning: "快速思考强度",
    defaultTier: "普通任务服务档位",
    fastTier: "mode=fast 服务档位",
    allowGroupCodex: "允许群聊 /ask",
    groupPlainText: "群聊普通文本作为任务",
    privatePlainText: "私聊普通文本作为任务",
    privatePollingFallback: "私聊轮询兜底",
    downloadIncomingMedia: "下载收到的媒体",
    acceptAny: "接受 @any",
    onlyRespondToBot: "群聊只回应 @bot",
    privateOnlyRespondToBot: "私聊只回应 @bot",
    dispatchToPeers: "Peer 转发",
    dispatchToPeersHint: "仅在配置了 peers.nodes 的多节点桥接部署中生效；没有 peer 节点时不会产生实际效果。",
    matchPresetAliases: "自动匹配可执行任务",
    resolveContacts: "通讯录辅助匹配用户",
    resolveContactsHint: "使用飞书通讯录资料匹配已配置的姓名、邮箱、手机号和别名；不影响 Open ID 精确匹配。",
    contactCacheTtl: "通讯录缓存秒数",
    sessionsEnabled: "连续会话",
    sessionMode: "会话模式",
    sessionModeContinuous: "连续模式",
    sessionModeTopic: "话题模式",
    topicReplyInThread: "使用飞书话题",
    queueWhileRunning: "运行中自动排队",
    editStatusMessage: "编辑状态消息",
    showDetailsByDefault: "默认显示细节",
    showProgressByDefault: "默认显示进度",
    progressMaxLines: "进度行数",
    statusInterval: "状态更新间隔",
    detectedRuntimeSkills: "运行时识别到的 Skills",
    detectedRuntimeModels: "运行时识别到的模型",
    noneDetected: "未识别到",
    accessDirectory: "访问目录",
    defaultPolicy: "默认模板",
    defaultTemplate: "新用户/群模板",
    permissionTemplates: "权限模板",
    permissionDefaults: "权限基线",
    permissionPreset: "模板",
    presetCustom: "自定义",
    identityPresetOption: "{label}",
    identityPresetNote: "模板定义可复用的完整权限配置。",
    syncedPermissionPreset: "跟随模板",
    templateOnly: "模板",
    templateOnlyHint: "模板只作为可复用配置，不按成员自动生效。",
    settingsOverrides: "配置",
    settingsOverridesHint: "运行字段留空时使用全局运行默认。",
    inheritDefault: "继承默认",
    assistantOverrides: "助手身份",
    modelOverrides: "模型默认值",
    runtimeOverrides: "运行默认值",
    replyOverrides: "回复可见性",
    addUser: "新增用户",
    addUserGroup: "新增模板",
    addGroup: "新增群聊",
    discoverAccess: "识别群/用户",
    discoveringAccess: "正在识别机器人所在群和群成员...",
    discoveredAccess: "识别到 {chats} 个群聊、{users} 个用户；已按默认模板加入草稿：新增 {newChats} 个群聊、{newUsers} 个用户，并更新 {updated} 个已有条目。",
    deleteAccessTarget: "删除此项",
    users: "用户",
    userGroups: "模板",
    groups: "群聊",
    chatGroups: "群聊",
    searchAccess: "搜索用户、用户组、群聊",
    noAccessMatches: "没有匹配的访问目标。",
    accessTarget: "访问目标",
    userKey: "用户键",
    userGroupKey: "模板键",
    groupKey: "群键",
    label: "显示标签",
    openIds: "匹配 Open ID",
    emails: "匹配邮箱",
    names: "匹配姓名",
    chatIds: "Chat ID",
    members: "成员键 / ID",
    aliases: "匹配别名",
    searchAliases: "搜索别名",
    unrestricted: "管理员无限制",
    allowCodex: "允许自由 /ask",
    accessModeHint: "在这里选择允许的主任务；自由任务和管理员无限制会作为虚拟任务参与自然语言路由。",
    taskPermissionHint: "此对象允许的手动和自动主任务；下方子任务覆盖可进一步收窄。",
    freeTaskLimitHint: "仅限制自由 /ask 请求；可执行任务会随任务自身携带需要的 Skills。",
    freeFormTask: "自由任务",
    unrestrictedTask: "管理员无限制",
    showDetails: "显示细节",
    showProgress: "显示进度",
    skills: "自由任务 Skills",
    models: "自由任务模型",
    tasks: "可执行任务",
    presetTasksJson: "可执行任务 JSON",
    executableTasks: "可执行任务",
    addExecutableTask: "新增任务",
    deleteExecutableTask: "删除任务",
    taskKey: "任务键",
    taskDescription: "说明",
    taskAliases: "别名",
    taskWorkspace: "工作区",
    taskRequiredSkills: "需要的 Skills",
    taskAllowedChats: "允许 Chat ID",
    taskAllowedSenders: "允许发送者 Open ID",
    taskOutputExpectations: "输出要求",
    taskPromptTemplate: "Prompt 模板",
    noExecutableTasks: "暂无可执行任务。",
    taskOverview: "任务整体说明",
    taskSubtasks: "响应子任务",
    taskExecution: "执行范围",
    taskBackground: "背景与要求",
    addSubtask: "新增子任务",
    deleteSubtask: "删除",
    subtaskId: "子任务 ID",
    subtaskLabel: "名称",
    subtaskType: "类型",
    subtaskManual: "手动任务",
    subtaskAutomatic: "自动任务",
    subtaskAliases: "触发别名",
    subtaskDescription: "说明",
    subtaskPrompt: "执行指令",
    subtaskSchedule: "触发条件",
    subtaskAction: "自动动作",
    automaticInput: "自动执行说明",
    subtaskOverrides: "子任务覆盖",
    manualSubtaskOverride: "允许手动执行的子任务",
    autoSubtaskOverride: "允许自动触发的子任务",
    restrictToChecked: "仅允许勾选项",
    scheduledTasks: "任务调度器",
    scheduledTasksHint: "自动任务在可执行任务的子任务里配置；群聊或策略必须在“允许自动触发的子任务”里显式勾选后才会触发。",
    scheduleGlobalEnabled: "启用自动子任务",
    scheduleTimezone: "调度时区",
    schedulePollInterval: "轮询间隔",
    addScheduledTask: "新增自动任务",
    deleteScheduledTask: "删除自动任务",
    noScheduledTasks: "暂无自动任务。",
    scheduleId: "自动任务 ID",
    scheduleKind: "动作",
    scheduleKindMessage: "发送消息",
    scheduleKindPresetTask: "执行可执行任务",
    scheduleTaskId: "可执行任务",
    scheduleWeekdays: "星期",
    scheduleTime: "时间",
    scheduleNoTime: "未设置",
    scheduleCatchup: "补执行窗口分钟数",
    minutes: "{count} 分钟",
    scheduleChatIds: "目标 Chat ID",
    scheduleMessage: "消息内容",
    scheduleInput: "任务输入",
    suppressNoopReply: "抑制无动作回复",
    scheduleTrigger: "触发",
    scheduleTarget: "目标",
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
    roundCompleted: "本轮完成",
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
    integrationDetail: "{state} · 当前用户登录启动 · {folder}",
    integrationDetailNoFolder: "{state} · 当前用户登录启动",
    startupTaskHint: "计划任务：{task}",
    startupAdminTaskHint: "管理员计划任务：{task}",
    startupShortcutHint: "启动文件夹快捷方式：{path}",
    noRecordedJobs: "没有记录的桥接任务。",
    noJobsYet: "暂无任务。",
    viewDetails: "查看详情",
    closeDetails: "关闭",
    loadingJobDetails: "正在加载任务详情...",
    jobDetails: "任务详情",
    jobMetadata: "元数据",
    jobFiles: "文件",
    inputAttachments: "输入附件",
    jobTimeline: "时间线",
    rawJobRecord: "原始任务记录",
    openFile: "打开文件",
    missingFile: "文件不存在",
    noPreview: "此文件类型暂无内联预览。",
    noAttachments: "没有下载到附件。",
    noEvents: "没有记录的时间线事件。",
    previewTruncated: "预览已截断。",
    bytes: "{count} 字节",
    attachments: "附件：{count}",
    noLogs: "暂无日志",
    codex: "执行器",
    codexHome: "Codex 目录",
    lark: "Lark",
    workspaces: "工作区",
    modalities: "模态",
    maxJobs: "最大任务数",
    routing: "路由",
    access: "访问控制",
    presetTasks: "可执行任务",
    eventDelivery: "事件接收",
    stateDir: "状态目录",
    logDir: "日志目录",
    startingConnection: "正在启动连接...",
    stoppingConnection: "正在关闭连接...",
    restartingDashboard: "正在重启面板...",
    restartingAll: "正在重启面板与连接...",
    connectionStarted: "连接已启动 · pid {pid}",
    connectionStopped: "连接已关闭 · pid {pid}",
    connectionAlreadyRunning: "连接已在运行 · pid {pid}",
    connectionNotRunning: "连接未运行。",
    dashboardRestarting: "面板正在重启，页面稍后会自动重新连接。",
    allRestarting: "面板与连接正在重启，页面稍后会自动重新连接。",
    applying: "正在应用...",
    updated: "已更新。",
    startMenuInstalled: "已添加“Feishu Codex Bridge Dashboard”和“Feishu Codex Bridge Stop”。可在 Windows 搜索或“所有应用”中找到；固定到开始页需要手动固定。",
    startMenuRemoved: "开始菜单快捷方式已移除。",
    dashboardStartupEnabled: "已启用登录时启动面板。",
    dashboardStartupAdminEnabled: "已使用管理员权限启用登录时启动面板。",
    dashboardStartupDisabled: "已关闭登录时启动面板。",
    connectionStartupEnabled: "已启用登录时启动连接。",
    connectionStartupAdminEnabled: "已使用管理员权限启用登录时启动连接。",
    connectionStartupDisabled: "已关闭登录时启动连接。",
    applyingAdmin: "正在等待管理员确认...",
    noChanges: "没有变更。",
    changed: "已变更：{keys}",
    skippedReadonly: "已跳过只读字段：{keys}",
    unsavedConfig: "有未保存变更，点击应用后才会写入配置。",
    restartRecommended: "建议重启",
    connectionRestartRecommended: "建议重启连接",
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
  configDraft: null,
  accessDirty: false,
  accessGroupsOpen: {
    global: true,
    user_group: true,
    identity: true,
    group: true,
  },
  selectedAccessTarget: "",
  accessSearch: "",
  selectedPresetTask: "",
  selectedScheduledTask: "",
  selectedJobId: "",
  loadingJobDetail: false,
  configEditing: false,
};

const fieldHelp = {
  en: {
    "codex.home_dir": "Local Codex configuration directory. Leave empty to use the default CODEX_HOME or user .codex directory.",
    "private.codex_sandbox": "Sandbox level used when launching local codex exec jobs.",
    "private.codex_timeout_sec": "Soft timeout for a Codex job before the bridge checks whether it should time out.",
    "private.codex_active_output_grace_sec": "When Codex stdout/stderr is still changing near timeout, keep waiting until output has been idle for this many seconds.",
    "private.codex_timeout_extension_sec": "Maximum extra seconds allowed after the normal timeout because output is still active.",
    "private.final_output_ready_sec": "Marks the current turn as final after --output-last-message has been written and stable for this many seconds. The process is kept alive for the idle window.",
    "private.final_output_idle_grace_sec": "How long to keep a Codex process alive after a final output while stdout/stderr/output files stay idle, so follow-up guidance can be queued before cleanup.",
    "jobs.max_concurrent": "Maximum number of bridge jobs allowed to run at the same time. Jobs in the same conversation still run sequentially.",
    "jobs.history_limit": "Number of terminal job records to keep after cleanup.",
    "jobs.auto_cleanup_enabled": "Automatically deletes old completed, failed, timed-out, and stopped jobs beyond the history limit.",
    "jobs.cleanup_delete_artifacts": "Also deletes saved job artifacts and downloaded files when old job history is cleaned.",
    "reply.max_chars": "Maximum characters sent directly in a Feishu reply before truncating or uploading the full output file.",
    "assistant.display_name": "Default name the bot should use in chat answers.",
    "assistant.identity_prompt": "Identity instruction injected into every Codex job before the user request.",
    "assistant.hide_internal_identity": "Tells the model not to volunteer Codex, model, CLI, bridge, job, session, or local-path details in final answers.",
    "models.default.model": "Model profile used for normal /ask jobs unless the message overrides it.",
    "models.default.reasoning_effort": "Default reasoning effort passed to Codex for normal jobs.",
    "models.default.service_tier": "Optional Codex service tier override for normal jobs. It does not affect mode=fast jobs.",
    "models.fast.model": "Model profile used when a message includes mode=fast.",
    "models.fast.reasoning_effort": "Reasoning effort used for mode=fast jobs.",
    "models.fast.service_tier": "Optional Codex service tier override used only when the message includes mode=fast.",
    "public.allow_codex": "Allows free-form Codex tasks from allowlisted group chats when sender policy also permits it.",
    "public.treat_all_text_as_codex": "Treats normal group messages as tasks. Keep off in noisy groups unless the chat is dedicated to the bridge.",
    "private.treat_all_text_as_codex": "Treats normal private bot messages as tasks without requiring /ask.",
    "private.polling_fallback_enabled": "Polls private chat history as a fallback if long-connection message events are unavailable.",
    "multimodal.download_incoming": "Downloads images, files, audio, and video resources from incoming messages when lark-cli can access them.",
    "routing.accept_any_target": "Allows /ask @any to be accepted by this bridge. Keep off when multiple bridge nodes may be listening.",
    "routing.only_respond_to_bot_mention": "In group chats, ignore messages unless they explicitly mention this bot.",
    "routing.private_only_respond_to_bot_mention": "In private chats, ignore messages unless they explicitly mention this bot.",
    "routing.dispatch_to_peers": "Reserved for multi-node deployments with peers.nodes configured. With no peers, it has no practical effect.",
    "access.default_template": "Template applied as the baseline for unknown senders and suggested for new users or chats.",
    "access.enable_preset_intent_matching": "Allows limited users to trigger approved executable tasks by alias or natural-language matching. Plain text is routed through the task matcher before execution.",
    "access.resolve_contacts_enabled": "Uses Feishu contact profiles to match configured names, emails, mobiles, and aliases. Open ID matching works without it.",
    "access.contact_cache_ttl_sec": "How long resolved contact profile values stay cached before the bridge queries Feishu again.",
    "sessions.enabled": "Stores conversation state so follow-up jobs can resume the previous Codex session.",
    "sessions.mode": "Continuous mode keeps one conversation per chat scope. Topic mode starts a separate conversation per Feishu topic/thread.",
    "sessions.topic_reply_in_thread": "In topic mode, sends the bridge status card as a Feishu thread reply when supported.",
    "sessions.queue_while_running": "Queues follow-ups while another job is running instead of rejecting them as busy.",
    "reply.edit_status_message": "Sends an interactive status card and edits it as the job moves from queued to running to final.",
    "reply.show_details_by_default": "Shows debug details such as job ID, workspace, model, and conversation key to everyone by default. Per-user/group Show Details settings can still enable them.",
    "reply.show_progress_by_default": "Shows short command/output progress summaries in status cards by default.",
    "reply.progress_max_lines": "Maximum progress lines shown in status cards.",
    "reply.status_update_interval_sec": "Minimum interval between automatic running-status card updates.",
    preset_tasks: "JSON definitions for approved executable tasks available to limited users.",
  },
  "zh-CN": {
    "codex.home_dir": "本地 Codex 配置目录；留空时使用默认 CODEX_HOME 或用户 .codex 目录。",
    "private.codex_sandbox": "启动本地 codex exec 任务时使用的沙箱级别。",
    "private.codex_timeout_sec": "Codex 任务普通超时时间；到点后会先判断输出是否仍在更新。",
    "private.codex_active_output_grace_sec": "接近超时时如果 Codex stdout/stderr 仍在更新，继续等到输出空闲这么多秒。",
    "private.codex_timeout_extension_sec": "因为输出仍活跃而允许超过普通超时的最大额外秒数。",
    "private.final_output_ready_sec": "--output-last-message 已写出并稳定指定秒数后，将当前轮标记为最终输出；进程会继续保留到空闲窗口结束。",
    "private.final_output_idle_grace_sec": "识别到最终输出后，stdout/stderr/output 持续空闲多久才清理 Codex 进程，用于给后续补充/引导留窗口。",
    "jobs.max_concurrent": "允许同时运行的桥接任务数；同一会话里的任务仍会串行执行。",
    "jobs.history_limit": "清理后保留的终态任务记录数量。",
    "jobs.auto_cleanup_enabled": "自动删除超出保留数量的完成、失败、超时和停止任务。",
    "jobs.cleanup_delete_artifacts": "清理旧任务历史时，同时删除任务产物和下载文件。",
    "reply.max_chars": "飞书回复中直接发送的最大字符数，超过后会截断或上传完整输出文件。",
    "assistant.display_name": "机器人在聊天回答中默认使用的身份名称。",
    "assistant.identity_prompt": "注入到每个 Codex 任务、位于用户请求之前的身份提示。",
    "assistant.hide_internal_identity": "让模型不要主动暴露 Codex、模型、CLI、桥接、job、session、本地路径等内部信息。",
    "models.default.model": "普通 /ask 任务默认使用的模型，除非消息里显式覆盖。",
    "models.default.reasoning_effort": "普通任务传给 Codex 的默认思考强度。",
    "models.default.service_tier": "普通任务的 Codex 服务档位覆盖项，可留空；不影响 mode=fast 任务。",
    "models.fast.model": "消息里使用 mode=fast 时的模型。",
    "models.fast.reasoning_effort": "mode=fast 任务使用的思考强度。",
    "models.fast.service_tier": "仅当消息里使用 mode=fast 时生效的 Codex 服务档位覆盖项，可留空。",
    "public.allow_codex": "允许白名单群聊发起自由 Codex 任务，仍会叠加发送者权限策略。",
    "public.treat_all_text_as_codex": "把群聊普通消息当作任务；除非是专用群，否则建议关闭。",
    "private.treat_all_text_as_codex": "私聊机器人时不用 /ask，普通文本也作为任务。",
    "private.polling_fallback_enabled": "长连接消息事件不可用时，轮询私聊历史作为兜底。",
    "multimodal.download_incoming": "当 lark-cli 有权限时，下载收到的图片、文件、音频和视频资源。",
    "routing.accept_any_target": "允许 /ask @any 被本桥接接受；多节点同时监听时建议关闭。",
    "routing.only_respond_to_bot_mention": "在群聊中只处理明确 @本机器人的消息。",
    "routing.private_only_respond_to_bot_mention": "在私聊中只处理明确 @本机器人的消息。",
    "routing.dispatch_to_peers": "预留给配置了 peers.nodes 的多节点部署；没有 peer 节点时没有实际效果。",
    "access.default_template": "作为未知发送者的基线权限，并作为新增用户或群聊时建议使用的模板。",
    "access.enable_preset_intent_matching": "允许受限用户通过别名或自然语言匹配触发已批准任务；普通消息会先进入任务匹配器判断是否适用。",
    "access.resolve_contacts_enabled": "使用飞书通讯录资料匹配已配置姓名、邮箱、手机号和别名；Open ID 精确匹配不依赖它。",
    "access.contact_cache_ttl_sec": "通讯录解析结果缓存时间，过期后会重新查询飞书。",
    "sessions.enabled": "保存会话状态，让后续任务可以 resume 上一次 Codex 会话。",
    "sessions.mode": "连续模式按聊天范围保持一个会话；话题模式按飞书话题/回复链拆分会话。",
    "sessions.topic_reply_in_thread": "话题模式下，尽量把桥接状态卡片发到飞书话题回复中。",
    "sessions.queue_while_running": "运行中收到后续消息时排队，而不是直接返回忙碌。",
    "reply.edit_status_message": "发送可编辑状态卡片，并在排队、运行、完成时更新同一张卡片。",
    "reply.show_details_by_default": "默认向所有人显示 job ID、工作区、模型、会话键等调试信息；访问目录中的用户/组/群聊“显示细节”仍可单独开启。",
    "reply.show_progress_by_default": "默认在状态卡片里显示简短执行/输出进度摘要。",
    "reply.progress_max_lines": "状态卡片最多显示的进度行数。",
    "reply.status_update_interval_sec": "运行中状态卡片自动更新的最小间隔。",
    preset_tasks: "给受限用户使用的已批准可执行任务 JSON 定义。",
  },
};

const GLOBAL_CONFIG_FIELDS = [
  "codex.home_dir",
  "private.codex_sandbox",
  "private.codex_timeout_sec",
  "private.codex_active_output_grace_sec",
  "private.codex_timeout_extension_sec",
  "private.final_output_ready_sec",
  "private.final_output_idle_grace_sec",
  "jobs.max_concurrent",
  "jobs.history_limit",
  "jobs.auto_cleanup_enabled",
  "jobs.cleanup_delete_artifacts",
  "reply.max_chars",
  "assistant.display_name",
  "assistant.hide_internal_identity",
  "assistant.identity_prompt",
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
  "routing.only_respond_to_bot_mention",
  "routing.private_only_respond_to_bot_mention",
  "routing.dispatch_to_peers",
  "access.default_template",
  "access.enable_preset_intent_matching",
  "access.resolve_contacts_enabled",
  "access.contact_cache_ttl_sec",
  "sessions.enabled",
  "sessions.mode",
  "sessions.topic_reply_in_thread",
  "sessions.queue_while_running",
  "reply.edit_status_message",
  "reply.show_details_by_default",
  "reply.show_progress_by_default",
  "reply.progress_max_lines",
  "reply.status_update_interval_sec",
  "preset_tasks",
  "task_scheduler",
];

const POLICY_PERMISSION_FIELDS = ["allow_codex", "unrestricted", "tasks", "skills", "models"];
const POLICY_SUBTASK_FIELDS = ["task_subtasks", "auto_subtasks"];
const TEMPLATE_CONFIG_FIELDS = POLICY_PERMISSION_FIELDS.concat(POLICY_SUBTASK_FIELDS, ["settings"]);
const FREE_FORM_TASK_ID = "__free_form__";
const UNRESTRICTED_TASK_ID = "__unrestricted__";

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

function escapeFormValue(value) {
  return String(value ?? "")
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
    round_completed: "roundCompleted",
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
  applyOptionHelp();
}

function rerenderFromCache() {
  if (state.lastStatus) renderStatus(state.lastStatus);
  if (state.lastJobs) renderJobs(state.lastJobs);
  if (state.lastLogs) renderLogs(state.lastLogs);
  if (state.lastConfigPayload && !isConfigInteracting()) renderConfig(state.lastConfigPayload);
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

function jobStatus(job) {
  if (text(job?.status).toLowerCase() === "running" && job?.final_message_ready) {
    return "round_completed";
  }
  return job?.display_status || job?.status || "unknown";
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

function formField(name) {
  const field = $("#configForm")?.elements?.namedItem(name);
  if (!field) return null;
  return typeof field.length === "number" && !field.closest ? field[0] : field;
}

function titleElementForField(field) {
  const label = field?.closest?.("label");
  if (!label) return null;
  const directSpan = Array.from(label.children).find((child) => child.tagName === "SPAN" && child.dataset.i18n);
  return directSpan || label.querySelector("span[data-i18n]");
}

function helpTextForField(name) {
  return (fieldHelp[state.lang] || fieldHelp.en)[name] || fieldHelp.en[name] || "";
}

function applyOptionHelp() {
  for (const name of Object.keys(fieldHelp.en)) {
    const field = formField(name);
    const title = titleElementForField(field);
    const helpText = helpTextForField(name);
    if (!title || !helpText || title.querySelector(".option-help")) continue;
    title.classList.add("field-title");
    const help = document.createElement("span");
    help.className = "option-help";
    help.tabIndex = 0;
    help.setAttribute("role", "button");
    help.setAttribute("aria-label", helpText);
    help.dataset.tooltip = helpText;
    help.textContent = "?";
    title.append(document.createTextNode(" "), help);
  }
}

function setConfigMessage(textValue) {
  document.querySelectorAll("[data-config-message]").forEach((element) => {
    element.textContent = textValue || "";
  });
}

function setConfigControlsWritable(writable) {
  const mutatingButtons = [
    '#configForm button[type="submit"]',
    "#addIdentityBtn",
    "#addUserGroupBtn",
    "#addGroupBtn",
    "#discoverAccessBtn",
    "#configTargetDetail [data-delete-access]",
    "#presetTaskEditor [data-add-preset-task]",
    "#presetTaskEditor [data-delete-preset-task]",
    "#scheduledTaskEditor [data-add-scheduled-task]",
    "#scheduledTaskEditor [data-delete-scheduled-task]",
  ].join(",");
  document.querySelectorAll(mutatingButtons).forEach((button) => {
    button.disabled = !writable;
  });
  document.querySelectorAll("#configForm input, #configForm select, #configForm textarea").forEach((field) => {
    field.disabled = !writable && field.id !== "configTargetSearch";
  });
}

function markConfigEditing() {
  state.configEditing = true;
  setConfigMessage(t("unsavedConfig"));
}

function isConfigInteracting() {
  const active = document.activeElement;
  return Boolean(
    state.configEditing ||
      (active && (active.closest?.("#configForm") || active.closest?.("#configWorkbench"))),
  );
}

function markAccessEditing() {
  state.accessDirty = true;
  markConfigEditing();
}

function isPolicyPermissionInput(target) {
  if (target.matches?.('[data-access-bool="allow_codex"], [data-access-bool="unrestricted"]')) return true;
  if (target.matches?.("[data-access-setting], [data-access-setting-bool]")) return true;
  return Boolean(
    target.closest?.('[data-choice-field="tasks"], [data-choice-field="skills"], [data-choice-field="models"], [data-subtask-override]') ||
      target.matches?.("[data-subtask-override-enabled]"),
  );
}

function markPermissionPresetCustom(target) {
  if (!isPolicyPermissionInput(target)) return;
  const card = target.closest?.("[data-access-kind]");
  const select = card?.querySelector?.("[data-policy-preset]");
  if (select) select.value = "custom";
}

function markAccessEditorDirty(event) {
  const target = event.target;
  if (!(target instanceof HTMLElement) || target.id === "configTargetSearch") return;
  if (
    target.matches("[data-access-field], [data-access-list], [data-access-bool], [data-access-setting], [data-access-setting-bool], [data-subtask-override-enabled]") ||
    target.closest("[data-choice-field], [data-subtask-override]")
  ) {
    markPermissionPresetCustom(target);
    markAccessEditing();
  }
}

function isConfigKeyWritable(key) {
  const allowlist = state.lastConfigPayload?.write_allowlist;
  return !Array.isArray(allowlist) || !allowlist.length || allowlist.includes(key);
}

function addConfigUpdate(updates, skipped, key, value) {
  if (isConfigKeyWritable(key)) {
    updates[key] = value;
  } else if (!skipped.includes(key)) {
    skipped.push(key);
  }
}

function runtimeModelOptions() {
  return state.lastStatus?.capabilities?.models || [];
}

function runtimeSkillOptions() {
  return state.lastStatus?.capabilities?.skills || [];
}

function optionId(value) {
  return typeof value === "string" ? value : value?.id || value?.model || value?.name || value?.slug;
}

function mergeOptionIds(...groups) {
  const result = [];
  for (const group of groups) {
    for (const item of group || []) {
      const value = String(optionId(item) || "").trim();
      if (value && !result.includes(value)) result.push(value);
    }
  }
  return result;
}

function modelIdsFromConfig(config = state.config || {}) {
  const models = getByPath(config, "models.available") || [];
  return mergeOptionIds(runtimeModelOptions(), models);
}

function modelSpeedTiers(items = []) {
  const tiers = [];
  for (const item of items || []) {
    if (!item || typeof item !== "object") continue;
    tiers.push(
      ...(Array.isArray(item.speed_tiers) ? item.speed_tiers : []),
      ...(Array.isArray(item.speedTiers) ? item.speedTiers : []),
      ...(Array.isArray(item.additional_speed_tiers) ? item.additional_speed_tiers : []),
    );
  }
  return tiers;
}

function serviceTierIdsFromConfig(config = state.configDraft || state.config || {}) {
  return mergeOptionIds(
    ["fast"],
    modelSpeedTiers(runtimeModelOptions()),
    modelSpeedTiers(getByPath(config, "models.available") || []),
    [
      getByPath(config, "models.default.service_tier"),
      getByPath(config, "models.fast.service_tier"),
    ],
  );
}

function workspaceIdsFromConfig(config = state.config || {}) {
  return Object.keys(getByPath(config, "workspaces") || {});
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

function renderServiceTierSelectOptions(config = state.configDraft || state.config || {}) {
  const ids = serviceTierIdsFromConfig(config);
  document.querySelectorAll("[data-service-tier-select]").forEach((select) => {
    const current = select.value || getByPath(config, select.name) || "";
    select.innerHTML = [`<option value="">${escapeHtml(t("config"))}</option>`]
      .concat(ids.map((id) => `<option value="${escapeHtml(id)}">${escapeHtml(id)}</option>`))
      .join("");
    if (current && !ids.includes(current)) {
      select.insertAdjacentHTML("beforeend", `<option value="${escapeHtml(current)}">${escapeHtml(current)}</option>`);
    }
    select.value = current || "";
  });
}

function optionIds(kind) {
  const config = state.configDraft || state.config || {};
  if (kind === "skills") return mergeOptionIds(runtimeSkillOptions(), getByPath(config, "skills.available") || []);
  if (kind === "models") return modelIdsFromConfig();
  if (kind === "tasks") return mergeOptionIds(Object.keys(getByPath(config, "preset_tasks") || {}), [FREE_FORM_TASK_ID, UNRESTRICTED_TASK_ID]);
  return [];
}

function renderRuntimeOptionsPreview() {
  const render = (id, labelKey, values) => {
    const container = $(id);
    if (!container) return;
    const ids = mergeOptionIds(values);
    container.innerHTML = `
      <span>${escapeHtml(t(labelKey))}</span>
      <div class="detected-option-list">
        ${
          ids.length
            ? ids.map((item) => `<code>${escapeHtml(item)}</code>`).join("")
            : `<em>${escapeHtml(t("noneDetected"))}</em>`
        }
      </div>
    `;
  };
  render("#detectedSkills", "detectedRuntimeSkills", runtimeSkillOptions());
  render("#detectedModels", "detectedRuntimeModels", runtimeModelOptions());
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

function choiceLabel(value) {
  if (value === FREE_FORM_TASK_ID) return t("freeFormTask");
  if (value === UNRESTRICTED_TASK_ID) return t("unrestrictedTask");
  return value;
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
              <span>${escapeHtml(choiceLabel(item))}</span>
            </label>
          `,
        )
        .join("")}
    </div>
  `;
}

function normalizeScheduleTime(value) {
  const match = String(value || "").trim().match(/^(\d{1,2}):(\d{2})$/);
  if (!match) return "";
  const hour = Number(match[1]);
  const minute = Number(match[2]);
  if (hour < 0 || hour > 23 || minute < 0 || minute > 59) return "";
  return `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
}

function scheduleTimeSelectHtml(value) {
  const current = normalizeScheduleTime(value);
  const options = [];
  for (let hour = 0; hour < 24; hour += 1) {
    for (const minute of [0, 15, 30, 45]) {
      options.push(`${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`);
    }
  }
  if (current && !options.includes(current)) options.push(current);
  return `
    <select data-subtask-schedule="time">
      <option value="" ${current ? "" : "selected"}>${escapeHtml(t("scheduleNoTime"))}</option>
      ${options
        .sort()
        .map((item) => `<option value="${escapeHtml(item)}" ${item === current ? "selected" : ""}>${escapeHtml(item)}</option>`)
        .join("")}
    </select>
  `;
}

function catchupSelectHtml(value) {
  const current = Number(value || 5);
  const options = [1, 3, 5, 10, 15, 30, 60];
  if (Number.isFinite(current) && current > 0 && !options.includes(current)) options.push(current);
  return `
    <select data-subtask-schedule-number="catch_up_minutes">
      ${options
        .sort((left, right) => left - right)
        .map((item) => `<option value="${item}" ${item === current ? "selected" : ""}>${escapeHtml(t("minutes", { count: item }))}</option>`)
        .join("")}
    </select>
  `;
}

function ensureConfigDraft() {
  if (!state.configDraft) state.configDraft = JSON.parse(JSON.stringify(state.config || {}));
  return state.configDraft;
}

function presetTaskDrafts() {
  const draft = ensureConfigDraft();
  let tasks = getByPath(draft, "preset_tasks");
  if (!tasks || typeof tasks !== "object" || Array.isArray(tasks)) {
    tasks = {};
    setByPath(draft, "preset_tasks", tasks);
  }
  return tasks;
}

function defaultPresetTask() {
  const workspace = workspaceIdsFromConfig(state.configDraft || state.config || {})[0] || "";
  return {
    enabled: true,
    description: "",
    background: "",
    aliases: [],
    workspace,
    subtasks: [],
    required_skills: [],
    allowed_chat_ids: [],
    allowed_sender_open_ids: [],
    output_expectations: "",
    prompt_template: "",
  };
}

function defaultTaskSubtask() {
  return {
    id: `subtask-${Date.now()}`,
    type: "manual",
    enabled: true,
    label: "",
    aliases: [],
    description: "",
    prompt: "",
  };
}

function normalizedTaskSubtasks(subtasks) {
  if (!Array.isArray(subtasks)) return [];
  return subtasks
    .map((item, index) => {
      if (item && typeof item === "object" && !Array.isArray(item)) {
        return {
          id: String(item.id || item.key || `subtask-${index + 1}`),
          type: String(item.type || "manual"),
          enabled: item.enabled !== false,
          label: item.label || item.name || "",
          aliases: listValue(item.aliases),
          description: item.description || "",
          prompt: item.prompt || item.instructions || "",
          schedule: item.schedule && typeof item.schedule === "object" && !Array.isArray(item.schedule) ? { ...item.schedule } : {},
          action: item.action && typeof item.action === "object" && !Array.isArray(item.action) ? { ...item.action } : {},
        };
      }
      const value = String(item || "").trim();
      return value
        ? {
            id: `subtask-${index + 1}`,
            type: "manual",
            enabled: true,
            label: value,
            aliases: [],
            description: value,
            prompt: "",
          }
        : null;
    })
    .filter(Boolean);
}

function taskSubtaskEditorHtml(subtasks) {
  const items = normalizedTaskSubtasks(subtasks);
  return `
    <div class="preset-task-head">
      <h5>${escapeHtml(t("taskSubtasks"))}</h5>
      <button type="button" class="secondary" data-add-subtask>${escapeHtml(t("addSubtask"))}</button>
    </div>
    ${
      items.length
        ? items
            .map((item, index) => {
              const schedule = item.schedule || {};
              const action = item.action || {};
              return `
                <details class="subtask-card" data-subtask-index="${index}">
                  <summary class="subtask-summary">
                    <span class="pill ${item.type === "automatic" ? "running" : "ok"}">${escapeHtml(item.type === "automatic" ? t("subtaskAutomatic") : t("subtaskManual"))}</span>
                    <strong>${escapeHtml(item.label || item.id || t("taskSubtasks"))}</strong>
                    <code>${escapeHtml(item.id || `subtask-${index + 1}`)}</code>
                    <span>${item.enabled === false ? escapeHtml(t("disabled")) : escapeHtml(t("enabled"))}</span>
                  </summary>
                  <div class="subtask-body">
                    <div class="access-card-head">
                    <label><span>${escapeHtml(t("subtaskId"))}</span><input data-subtask-field="id" value="${escapeFormValue(item.id || "")}" /></label>
                    <label><span>${escapeHtml(t("subtaskLabel"))}</span><input data-subtask-field="label" value="${escapeFormValue(item.label || "")}" /></label>
                    </div>
                    <div class="access-card-grid">
                    <label>
                      <span>${escapeHtml(t("subtaskType"))}</span>
                      <select data-subtask-field="type">
                        <option value="manual" ${item.type === "automatic" ? "" : "selected"}>${escapeHtml(t("subtaskManual"))}</option>
                        <option value="automatic" ${item.type === "automatic" ? "selected" : ""}>${escapeHtml(t("subtaskAutomatic"))}</option>
                      </select>
                    </label>
                    <label class="check"><input data-subtask-bool="enabled" type="checkbox" ${item.enabled === false ? "" : "checked"} /><span>${escapeHtml(t("enabled"))}</span></label>
                    </div>
                    <label><span>${escapeHtml(t("subtaskAliases"))}</span><textarea data-subtask-list="aliases" rows="2">${escapeFormValue(listValue(item.aliases).join("\n"))}</textarea></label>
                    <label><span>${escapeHtml(t("subtaskDescription"))}</span><textarea data-subtask-field="description" rows="2">${escapeFormValue(item.description || "")}</textarea></label>
                    <label><span>${escapeHtml(t("subtaskPrompt"))}</span><textarea data-subtask-field="prompt" rows="3">${escapeFormValue(item.prompt || "")}</textarea></label>
                    ${
                    item.type === "automatic"
                      ? `
                        <div class="access-card-grid">
                          <div class="schedule-field">
                            <strong>${escapeHtml(t("scheduleWeekdays"))}</strong>
                            ${weekdayChoiceGroup(schedule.weekdays, "data-subtask-schedule-list-choice")}
                          </div>
                          <label><span>${escapeHtml(t("scheduleTime"))}</span>${scheduleTimeSelectHtml(schedule.time || "")}</label>
                          <label><span>${escapeHtml(t("scheduleCatchup"))}</span>${catchupSelectHtml(schedule.catch_up_minutes ?? 5)}</label>
                          <label class="check"><input data-subtask-action-bool="suppress_noop_reply" type="checkbox" ${action.suppress_noop_reply === false ? "" : "checked"} /><span>${escapeHtml(t("suppressNoopReply"))}</span></label>
                        </div>
                        <label><span>${escapeHtml(t("automaticInput"))}</span><textarea data-subtask-action="input" rows="3">${escapeFormValue(action.input || action.message || "")}</textarea></label>
                      `
                      : ""
                    }
                    <div class="access-card-toolbar">
                    <span></span>
                    <button type="button" class="secondary danger" data-delete-subtask="${index}">${escapeHtml(t("deleteSubtask"))}</button>
                    </div>
                  </div>
                </details>
              `;
            })
            .join("")
        : `<p class="empty-copy">${escapeHtml(t("taskSubtasks"))}</p>`
    }
  `;
}

function syncPresetTasksTextarea() {
  const field = document.querySelector('[name="preset_tasks"]');
  if (!field) return;
  const tasks = getByPath(state.configDraft || state.config || {}, "preset_tasks") || {};
  field.value = JSON.stringify(tasks, null, 2);
}

function selectedPresetTaskKey(tasks) {
  const keys = Object.keys(tasks || {}).sort();
  if (state.selectedPresetTask && keys.includes(state.selectedPresetTask)) return state.selectedPresetTask;
  state.selectedPresetTask = keys[0] || "";
  return state.selectedPresetTask;
}

function workspaceSelectHtml(value) {
  const ids = workspaceIdsFromConfig(state.configDraft || state.config || {});
  const options = [`<option value="">${escapeHtml(t("config"))}</option>`].concat(
    ids.map((id) => `<option value="${escapeHtml(id)}" ${id === value ? "selected" : ""}>${escapeHtml(id)}</option>`),
  );
  if (value && !ids.includes(value)) {
    options.push(`<option value="${escapeHtml(value)}" selected>${escapeHtml(value)}</option>`);
  }
  return `<select data-task-field="workspace">${options.join("")}</select>`;
}

function presetTaskDetailHtml(key, task = {}) {
  return `
    <section class="preset-task-detail" id="presetTaskDetail" data-original-key="${escapeHtml(key)}">
      <div class="task-section">
        <h5>${escapeHtml(t("taskOverview"))}</h5>
        <div class="access-card-head">
          <label>
            <span>${escapeHtml(t("taskKey"))}</span>
            <input data-task-field="key" value="${escapeFormValue(key)}" />
          </label>
          <label>
            <span>${escapeHtml(t("taskDescription"))}</span>
            <input data-task-field="description" value="${escapeFormValue(task.description || "")}" />
          </label>
        </div>
        <div class="access-toggles">
          <label class="check"><input data-task-bool="enabled" type="checkbox" ${task.enabled === false ? "" : "checked"} /><span>${escapeHtml(t("enabled"))}</span></label>
        </div>
        <div class="access-card-grid">
          <label>
            <span>${escapeHtml(t("taskAliases"))}</span>
            <textarea data-task-list="aliases" rows="3">${escapeFormValue(listValue(task.aliases).join("\n"))}</textarea>
          </label>
          <label>
            <span>${escapeHtml(t("taskWorkspace"))}</span>
            ${workspaceSelectHtml(String(task.workspace || ""))}
          </label>
        </div>
        <label>
          <span>${escapeHtml(t("taskBackground"))}</span>
          <textarea data-task-field="background" rows="4">${escapeFormValue(task.background || "")}</textarea>
        </label>
      </div>
      <div class="task-section">
        ${taskSubtaskEditorHtml(task.subtasks)}
      </div>
      <div class="task-section">
        <h5>${escapeHtml(t("taskExecution"))}</h5>
        <div class="access-card-grid">
          <label>
            <span>${escapeHtml(t("taskAllowedChats"))}</span>
            <textarea data-task-list="allowed_chat_ids" rows="3">${escapeFormValue(listValue(task.allowed_chat_ids).join("\n"))}</textarea>
          </label>
          <label>
            <span>${escapeHtml(t("taskAllowedSenders"))}</span>
            <textarea data-task-list="allowed_sender_open_ids" rows="3">${escapeFormValue(listValue(task.allowed_sender_open_ids).join("\n"))}</textarea>
          </label>
        </div>
        <div class="access-permissions">
          <div><strong>${escapeHtml(t("taskRequiredSkills"))}</strong>${choiceGroup("required_skills", task.required_skills, optionIds("skills"))}</div>
        </div>
        <div class="access-card-grid">
          <label>
            <span>${escapeHtml(t("taskOutputExpectations"))}</span>
            <textarea data-task-field="output_expectations" rows="3">${escapeFormValue(task.output_expectations || "")}</textarea>
          </label>
          <label>
            <span>${escapeHtml(t("taskPromptTemplate"))}</span>
            <textarea data-task-field="prompt_template" rows="5">${escapeFormValue(task.prompt_template || "")}</textarea>
          </label>
        </div>
      </div>
      <div class="access-card-toolbar">
        <span></span>
        <button type="button" class="secondary danger" data-delete-preset-task>${escapeHtml(t("deleteExecutableTask"))}</button>
      </div>
    </section>
  `;
}

function presetTaskEditorHtml(tasks, selectedKey) {
  const keys = Object.keys(tasks || {}).sort();
  return `
    <div class="preset-task-head">
      <h4>${escapeHtml(t("executableTasks"))}</h4>
      <button type="button" class="secondary" data-add-preset-task>${escapeHtml(t("addExecutableTask"))}</button>
    </div>
    ${
      keys.length
        ? `<div class="preset-task-layout">
            <div class="preset-task-list">
              ${keys
                .map((key) => {
                  const task = tasks[key] || {};
                  return `
                    <button type="button" class="access-target ${key === selectedKey ? "active" : ""}" data-preset-task="${escapeHtml(key)}">
                      <span>${task.enabled === false ? escapeHtml(t("disabled")) : escapeHtml(t("enabled"))}</span>
                      <strong>${escapeHtml(task.description || key)}</strong>
                      <code>${escapeHtml(key)}</code>
                    </button>
                  `;
                })
                .join("")}
            </div>
            ${selectedKey ? presetTaskDetailHtml(selectedKey, tasks[selectedKey] || {}) : ""}
          </div>`
        : `<p class="empty-copy">${escapeHtml(t("noExecutableTasks"))}</p>`
    }
  `;
}

function collectTaskSubtasks(detail) {
  return Array.from(detail.querySelectorAll("[data-subtask-index]")).map((card, index) => {
    const item = { id: `subtask-${index + 1}`, type: "manual", enabled: true, aliases: [] };
    card.querySelectorAll("[data-subtask-field]").forEach((field) => {
      const name = field.dataset.subtaskField;
      const value = String(field.value || "").trim();
      if (value) item[name] = value;
      else delete item[name];
    });
    card.querySelectorAll("[data-subtask-list]").forEach((field) => {
      item[field.dataset.subtaskList] = splitLines(field.value);
    });
    card.querySelectorAll("[data-subtask-bool]").forEach((field) => {
      item[field.dataset.subtaskBool] = Boolean(field.checked);
    });
    if (item.type === "automatic") {
      const schedule = {};
      card.querySelectorAll("[data-subtask-schedule]").forEach((field) => {
        const value = String(field.value || "").trim();
        if (value) schedule[field.dataset.subtaskSchedule] = value;
      });
      card.querySelectorAll("[data-subtask-schedule-number]").forEach((field) => {
        const value = String(field.value || "").trim();
        if (value) schedule[field.dataset.subtaskScheduleNumber] = Number(value);
      });
      card.querySelectorAll("[data-subtask-schedule-list]").forEach((field) => {
        schedule[field.dataset.subtaskScheduleList] = splitLines(field.value);
      });
      card.querySelectorAll("[data-subtask-schedule-list-choice]").forEach((group) => {
        schedule[group.dataset.subtaskScheduleListChoice] = Array.from(group.querySelectorAll("input:checked")).map((input) => input.value);
      });
      const action = {};
      card.querySelectorAll("[data-subtask-action]").forEach((field) => {
        const value = String(field.value || "").trim();
        if (value) action[field.dataset.subtaskAction] = value;
      });
      card.querySelectorAll("[data-subtask-action-bool]").forEach((field) => {
        action[field.dataset.subtaskActionBool] = Boolean(field.checked);
      });
      const cleanedSchedule = pruneEmptyObject(schedule);
      const cleanedAction = pruneEmptyObject(action);
      if (Object.keys(cleanedSchedule).length) item.schedule = cleanedSchedule;
      if (Object.keys(cleanedAction).length) item.action = cleanedAction;
    }
    return item;
  });
}

function syncPresetTaskDetail() {
  const detail = $("#presetTaskDetail");
  if (!detail) return;
  const tasks = presetTaskDrafts();
  const originalKey = detail.dataset.originalKey || "";
  const keyField = detail.querySelector('[data-task-field="key"]');
  const key = String(keyField?.value || "").trim() || originalKey;
  if (!key) return;
  const existing = tasks[originalKey] || tasks[key] || defaultPresetTask();
  const item = JSON.parse(JSON.stringify(existing));
  detail.querySelectorAll("[data-task-field]").forEach((field) => {
    const name = field.dataset.taskField;
    if (name === "key") return;
    const value = String(field.value || "").trim();
    if (value) item[name] = value;
    else delete item[name];
  });
  detail.querySelectorAll("[data-task-list]").forEach((field) => {
    item[field.dataset.taskList] = splitLines(field.value);
  });
  detail.querySelectorAll("[data-task-bool]").forEach((field) => {
    item[field.dataset.taskBool] = Boolean(field.checked);
  });
  detail.querySelectorAll("[data-choice-field]").forEach((group) => {
    item[group.dataset.choiceField] = Array.from(group.querySelectorAll("input:checked")).map((input) => input.value);
  });
  item.subtasks = collectTaskSubtasks(detail);
  if (originalKey && originalKey !== key) delete tasks[originalKey];
  tasks[key] = item;
  state.selectedPresetTask = key;
  syncPresetTasksTextarea();
}

function removeTaskReferences(taskId) {
  if (!taskId) return;
  ensureAccessDraft();
  const clearItem = (item) => {
    if (Array.isArray(item?.tasks) && item.tasks.includes(taskId)) {
      item.tasks = item.tasks.filter((value) => value !== taskId);
      state.accessDirty = true;
    }
  };
  clearItem(state.accessDraft.default_policy);
  for (const kind of ["identity", "user_group", "group"]) {
    for (const item of Object.values(state.accessDraft[kind] || {})) clearItem(item);
  }
}

function renderPresetTaskEditor() {
  const container = $("#presetTaskEditor");
  if (!container) return;
  const tasks = presetTaskDrafts();
  const selectedKey = selectedPresetTaskKey(tasks);
  container.innerHTML = presetTaskEditorHtml(tasks, selectedKey);
  container.querySelector("[data-add-preset-task]")?.addEventListener("click", (event) => {
    event.preventDefault();
    syncPresetTaskDetail();
    const draftTasks = presetTaskDrafts();
    const key = `task-${Date.now()}`;
    draftTasks[key] = defaultPresetTask();
    state.selectedPresetTask = key;
    markConfigEditing();
    syncPresetTasksTextarea();
    renderPresetTaskEditor();
  });
  container.querySelectorAll("[data-preset-task]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      syncPresetTaskDetail();
      state.selectedPresetTask = button.dataset.presetTask;
      renderPresetTaskEditor();
    });
  });
  container.querySelector("[data-delete-preset-task]")?.addEventListener("click", (event) => {
    event.preventDefault();
    const key = selectedPresetTaskKey(presetTaskDrafts());
    if (!key) return;
    const tasks = presetTaskDrafts();
    delete tasks[key];
    removeTaskReferences(key);
    state.selectedPresetTask = "";
    markConfigEditing();
    syncPresetTasksTextarea();
    renderPresetTaskEditor();
  });
  container.querySelector("[data-add-subtask]")?.addEventListener("click", (event) => {
    event.preventDefault();
    syncPresetTaskDetail();
    const tasks = presetTaskDrafts();
    const key = selectedPresetTaskKey(tasks);
    if (!key) return;
    const task = tasks[key] || defaultPresetTask();
    task.subtasks = normalizedTaskSubtasks(task.subtasks);
    task.subtasks.push(defaultTaskSubtask());
    tasks[key] = task;
    markConfigEditing();
    syncPresetTasksTextarea();
    renderPresetTaskEditor();
  });
  container.querySelectorAll("[data-delete-subtask]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      syncPresetTaskDetail();
      const tasks = presetTaskDrafts();
      const key = selectedPresetTaskKey(tasks);
      if (!key) return;
      const index = Number(button.dataset.deleteSubtask);
      const task = tasks[key] || defaultPresetTask();
      task.subtasks = normalizedTaskSubtasks(task.subtasks).filter((_, itemIndex) => itemIndex !== index);
      tasks[key] = task;
      markConfigEditing();
      syncPresetTasksTextarea();
      renderPresetTaskEditor();
    });
  });
  container.querySelectorAll('[data-subtask-field="type"]').forEach((field) => {
    field.addEventListener("change", () => {
      syncPresetTaskDetail();
      markConfigEditing();
      renderPresetTaskEditor();
    });
  });
  container.querySelectorAll("[data-task-field], [data-task-list], [data-task-bool], [data-choice-field] input, [data-subtask-field], [data-subtask-list], [data-subtask-bool], [data-subtask-schedule], [data-subtask-schedule-number], [data-subtask-schedule-list], [data-subtask-schedule-list-choice] input, [data-subtask-action], [data-subtask-action-bool]").forEach((field) => {
    const eventName = field.matches?.("input, textarea") ? "input" : "change";
    field.addEventListener(eventName, () => {
      markConfigEditing();
    });
  });
  syncPresetTasksTextarea();
}

function scheduledTasksDraft() {
  const draft = ensureConfigDraft();
  let scheduled = getByPath(draft, "task_scheduler");
  if (!scheduled || typeof scheduled !== "object" || Array.isArray(scheduled)) {
    scheduled = { enabled: false, timezone: "Asia/Shanghai", poll_interval_sec: 30 };
    setByPath(draft, "task_scheduler", scheduled);
  }
  return scheduled;
}

function defaultScheduledTask() {
  return {
    id: `auto-task-${Date.now()}`,
    enabled: false,
    kind: "message",
    chat_ids: [],
    weekdays: [],
    time: "",
    catch_up_minutes: 5,
    message: "",
    suppress_noop_reply: true,
  };
}

function syncScheduledTasksTextarea() {
  const field = document.querySelector('[name="task_scheduler"]');
  if (!field) return;
  field.value = JSON.stringify(getByPath(state.configDraft || state.config || {}, "task_scheduler") || {}, null, 2);
}

function selectedScheduledTaskId(items) {
  const ids = (items || []).map((item) => String(item.id || "")).filter(Boolean);
  if (state.selectedScheduledTask && ids.includes(state.selectedScheduledTask)) return state.selectedScheduledTask;
  state.selectedScheduledTask = ids[0] || "";
  return state.selectedScheduledTask;
}

function weekdayLabel(value) {
  const labels =
    state.lang === "zh-CN"
      ? { mon: "周一", tue: "周二", wed: "周三", thu: "周四", fri: "周五", sat: "周六", sun: "周日" }
      : { mon: "Mon", tue: "Tue", wed: "Wed", thu: "Thu", fri: "Fri", sat: "Sat", sun: "Sun" };
  return labels[String(value || "").toLowerCase()] || value;
}

function scheduledTaskSummary(item) {
  const weekdays = listValue(item.weekdays).map(weekdayLabel).join(", ") || "-";
  const time = item.time || "--:--";
  const chats = listValue(item.chat_ids).length || 0;
  const action = item.kind === "preset_task" ? `${t("scheduleKindPresetTask")}: ${item.task_id || "-"}` : t("scheduleKindMessage");
  return `${t("scheduleTrigger")}: ${weekdays} ${time} · ${action} · ${t("scheduleTarget")}: ${chats}`;
}

function weekdayChoiceGroup(selected, dataAttr = "data-schedule-list-choice") {
  const values = new Set(listValue(selected));
  const options = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
  return `
    <div class="choice-group" ${dataAttr}="weekdays">
      ${options
        .map(
          (item) => `
            <label class="chip-check">
              <input type="checkbox" value="${escapeHtml(item)}" ${values.has(item) ? "checked" : ""} />
              <span>${escapeHtml(weekdayLabel(item))}</span>
            </label>
          `,
        )
        .join("")}
    </div>
  `;
}

function scheduledTaskDetailHtml(item = {}) {
  const taskIds = Object.keys(presetTaskDrafts()).sort();
  const taskOptions = [`<option value="">${escapeHtml(t("config"))}</option>`].concat(
    taskIds.map((id) => `<option value="${escapeHtml(id)}" ${id === item.task_id ? "selected" : ""}>${escapeHtml(id)}</option>`),
  );
  if (item.task_id && !taskIds.includes(item.task_id)) {
    taskOptions.push(`<option value="${escapeHtml(item.task_id)}" selected>${escapeHtml(item.task_id)}</option>`);
  }
  return `
    <section class="scheduled-task-detail" id="scheduledTaskDetail" data-original-id="${escapeHtml(item.id || "")}">
      <div class="task-section">
        <h5>${escapeHtml(t("taskOverview"))}</h5>
        <div class="access-card-head">
          <label>
            <span>${escapeHtml(t("scheduleId"))}</span>
            <input data-schedule-field="id" value="${escapeFormValue(item.id || "")}" />
          </label>
          <label>
            <span>${escapeHtml(t("scheduleKind"))}</span>
            <select data-schedule-field="kind">
              <option value="message" ${item.kind === "preset_task" ? "" : "selected"}>${escapeHtml(t("scheduleKindMessage"))}</option>
              <option value="preset_task" ${item.kind === "preset_task" ? "selected" : ""}>${escapeHtml(t("scheduleKindPresetTask"))}</option>
            </select>
          </label>
        </div>
        <div class="access-toggles">
          <label class="check"><input data-schedule-bool="enabled" type="checkbox" ${item.enabled === true ? "checked" : ""} /><span>${escapeHtml(t("enabled"))}</span></label>
          <label class="check"><input data-schedule-bool="suppress_noop_reply" type="checkbox" ${item.suppress_noop_reply ? "checked" : ""} /><span>${escapeHtml(t("suppressNoopReply"))}</span></label>
        </div>
      </div>
      <div class="task-section">
        <h5>${escapeHtml(t("scheduleTrigger"))}</h5>
        <div class="access-card-grid">
          <label>
            <span>${escapeHtml(t("scheduleTime"))}</span>
            <input data-schedule-field="time" type="time" value="${escapeFormValue(item.time || "")}" />
          </label>
          <label>
            <span>${escapeHtml(t("scheduleCatchup"))}</span>
            <input data-schedule-number="catch_up_minutes" type="number" min="1" max="60" step="1" value="${escapeFormValue(item.catch_up_minutes ?? 5)}" />
          </label>
        </div>
        <div>
          <strong>${escapeHtml(t("scheduleWeekdays"))}</strong>
          ${weekdayChoiceGroup(item.weekdays)}
        </div>
      </div>
      <div class="task-section">
        <h5>${escapeHtml(t("scheduleTarget"))}</h5>
        <label>
          <span>${escapeHtml(t("scheduleChatIds"))}</span>
          <textarea data-schedule-list="chat_ids" rows="3">${escapeFormValue(listValue(item.chat_ids).join("\n"))}</textarea>
        </label>
      </div>
      <div class="task-section">
        <h5>${escapeHtml(t("scheduleKind"))}</h5>
        <div class="access-card-grid">
          <label>
            <span>${escapeHtml(t("scheduleTaskId"))}</span>
            <select data-schedule-field="task_id">${taskOptions.join("")}</select>
          </label>
          <label>
            <span>${escapeHtml(t("scheduleMessage"))}</span>
            <textarea data-schedule-field="message" rows="3">${escapeFormValue(item.message || "")}</textarea>
          </label>
        </div>
        <label>
          <span>${escapeHtml(t("scheduleInput"))}</span>
          <textarea data-schedule-field="input" rows="5">${escapeFormValue(item.input || "")}</textarea>
        </label>
      </div>
      <div class="access-card-toolbar">
        <span></span>
        <button type="button" class="secondary danger" data-delete-scheduled-task>${escapeHtml(t("deleteScheduledTask"))}</button>
      </div>
    </section>
  `;
}

function scheduledTaskEditorHtml(scheduled) {
  return `
    <div class="preset-task-head">
      <div>
        <h4>${escapeHtml(t("scheduledTasks"))}</h4>
        <p class="access-default-copy">${escapeHtml(t("scheduledTasksHint"))}</p>
      </div>
    </div>
    <div class="scheduled-global">
      <label class="check"><input data-schedule-global-bool="enabled" type="checkbox" ${scheduled.enabled ? "checked" : ""} /><span>${escapeHtml(t("scheduleGlobalEnabled"))}</span></label>
      <label><span>${escapeHtml(t("scheduleTimezone"))}</span><input data-schedule-global="timezone" value="${escapeFormValue(scheduled.timezone || "Asia/Shanghai")}" /></label>
      <label><span>${escapeHtml(t("schedulePollInterval"))}</span><input data-schedule-global-number="poll_interval_sec" type="number" min="10" step="10" value="${escapeFormValue(scheduled.poll_interval_sec || 30)}" /></label>
    </div>
  `;
}

function syncScheduledTaskDetail() {
  const container = $("#scheduledTaskEditor");
  if (!container) return;
  const scheduled = scheduledTasksDraft();
  container.querySelectorAll("[data-schedule-global]").forEach((field) => {
    const value = String(field.value || "").trim();
    if (value) scheduled[field.dataset.scheduleGlobal] = value;
    else delete scheduled[field.dataset.scheduleGlobal];
  });
  container.querySelectorAll("[data-schedule-global-number]").forEach((field) => {
    scheduled[field.dataset.scheduleGlobalNumber] = Number(field.value || 0);
  });
  container.querySelectorAll("[data-schedule-global-bool]").forEach((field) => {
    scheduled[field.dataset.scheduleGlobalBool] = Boolean(field.checked);
  });
  const detail = $("#scheduledTaskDetail");
  if (!detail) {
    syncScheduledTasksTextarea();
    return;
  }
  const originalId = detail.dataset.originalId || "";
  const items = scheduled.items || [];
  const index = items.findIndex((item) => String(item.id || "") === originalId);
  const item = JSON.parse(JSON.stringify(index >= 0 ? items[index] : defaultScheduledTask()));
  detail.querySelectorAll("[data-schedule-field]").forEach((field) => {
    const name = field.dataset.scheduleField;
    const value = String(field.value || "").trim();
    if (value) item[name] = value;
    else delete item[name];
  });
  detail.querySelectorAll("[data-schedule-number]").forEach((field) => {
    item[field.dataset.scheduleNumber] = Number(field.value || 0);
  });
  detail.querySelectorAll("[data-schedule-list]").forEach((field) => {
    item[field.dataset.scheduleList] = splitLines(field.value);
  });
  detail.querySelectorAll("[data-schedule-list-choice]").forEach((group) => {
    item[group.dataset.scheduleListChoice] = Array.from(group.querySelectorAll("input:checked")).map((input) => input.value);
  });
  detail.querySelectorAll("[data-schedule-bool]").forEach((field) => {
    item[field.dataset.scheduleBool] = Boolean(field.checked);
  });
  if (!item.id) item.id = originalId || `auto-task-${Date.now()}`;
  if (index >= 0) items[index] = item;
  else items.push(item);
  state.selectedScheduledTask = item.id;
  syncScheduledTasksTextarea();
}

function renderScheduledTaskEditor() {
  const container = $("#scheduledTaskEditor");
  if (!container) return;
  const scheduled = scheduledTasksDraft();
  container.innerHTML = scheduledTaskEditorHtml(scheduled);
  container.querySelector("[data-add-scheduled-task]")?.addEventListener("click", (event) => {
    event.preventDefault();
    syncScheduledTaskDetail();
    const draft = scheduledTasksDraft();
    const item = defaultScheduledTask();
    draft.items.push(item);
    state.selectedScheduledTask = item.id;
    markConfigEditing();
    syncScheduledTasksTextarea();
    renderScheduledTaskEditor();
  });
  container.querySelectorAll("[data-scheduled-task]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      syncScheduledTaskDetail();
      state.selectedScheduledTask = button.dataset.scheduledTask;
      renderScheduledTaskEditor();
    });
  });
  container.querySelector("[data-delete-scheduled-task]")?.addEventListener("click", (event) => {
    event.preventDefault();
    const scheduled = scheduledTasksDraft();
    const id = selectedScheduledTaskId(scheduled.items);
    scheduled.items = (scheduled.items || []).filter((item) => String(item.id || "") !== id);
    state.selectedScheduledTask = "";
    markConfigEditing();
    syncScheduledTasksTextarea();
    renderScheduledTaskEditor();
  });
  container.querySelectorAll("[data-schedule-global], [data-schedule-global-number], [data-schedule-global-bool], [data-schedule-field], [data-schedule-number], [data-schedule-list], [data-schedule-bool], [data-schedule-list-choice] input").forEach((field) => {
    const eventName = field.matches?.("input, textarea") ? "input" : "change";
    field.addEventListener(eventName, () => markConfigEditing());
  });
  syncScheduledTasksTextarea();
}

function optionTags(options, selected, includeInherit = true) {
  const value = String(selected ?? "");
  const unique = mergeOptionIds(options);
  if (value && !unique.includes(value)) unique.push(value);
  return [
    includeInherit ? `<option value="">${escapeHtml(t("inheritDefault"))}</option>` : "",
    ...unique.map((item) => `<option value="${escapeHtml(item)}" ${item === value ? "selected" : ""}>${escapeHtml(item)}</option>`),
  ].join("");
}

function settingValue(item, path) {
  if (path === "reply.show_details" && typeof item.show_details === "boolean") return item.show_details;
  if (path === "reply.show_progress" && typeof item.show_progress === "boolean") return item.show_progress;
  return getByPath(item.settings || {}, path);
}

function globalSettingValue(path) {
  return getByPath(state.config || {}, path);
}

function accessTextSetting(path, item, labelKey, rows = 0) {
  const value = settingValue(item, path);
  const placeholder = globalSettingValue(path);
  const common = `data-access-setting="${escapeHtml(path)}" placeholder="${escapeFormValue(placeholder ?? t("inheritDefault"))}"`;
  if (rows) {
    return `<label class="wide"><span>${escapeHtml(t(labelKey))}</span><textarea ${common} rows="${rows}">${escapeFormValue(value ?? "")}</textarea></label>`;
  }
  return `<label><span>${escapeHtml(t(labelKey))}</span><input ${common} value="${escapeFormValue(value ?? "")}" /></label>`;
}

function accessNumberSetting(path, item, labelKey, attrs = "") {
  const value = settingValue(item, path);
  const placeholder = globalSettingValue(path);
  const common = `data-access-setting="${escapeHtml(path)}" type="number" ${attrs} placeholder="${escapeFormValue(placeholder ?? t("inheritDefault"))}"`;
  return `<label><span>${escapeHtml(t(labelKey))}</span><input ${common} value="${escapeFormValue(value ?? "")}" /></label>`;
}

function accessSelectSetting(path, item, labelKey, options) {
  const value = settingValue(item, path);
  return `
    <label>
      <span>${escapeHtml(t(labelKey))}</span>
      <select data-access-setting="${escapeHtml(path)}">${optionTags(options, value)}</select>
    </label>
  `;
}

function accessBoolSetting(path, item, labelKey) {
  const value = settingValue(item, path);
  const normalized = typeof value === "boolean" ? String(value) : "";
  return `
    <label>
      <span>${escapeHtml(t(labelKey))}</span>
      <select data-access-setting-bool="${escapeHtml(path)}">
        <option value="" ${normalized === "" ? "selected" : ""}>${escapeHtml(t("inheritDefault"))}</option>
        <option value="true" ${normalized === "true" ? "selected" : ""}>${escapeHtml(t("enabled"))}</option>
        <option value="false" ${normalized === "false" ? "selected" : ""}>${escapeHtml(t("disabled"))}</option>
      </select>
    </label>
  `;
}

function accessPath(kind) {
  return {
    default_policy: "access.default_policy",
    identity: "access.identities",
    user_group: "access.user_groups",
    group: "access.groups",
  }[kind];
}

function accessKindLabel(kind) {
  return {
    global: t("defaultConfig"),
    default_policy: t("defaultPolicy"),
    identity: t("users"),
    user_group: t("userGroups"),
    group: t("chatGroups"),
  }[kind] || kind;
}

function accessGroupKind(kind) {
  return kind === "global" || kind === "default_policy" ? "global" : kind;
}

function accessGroupLabel(kind) {
  return {
    global: t("globalAndDefaults"),
    user_group: t("userGroups"),
    identity: t("users"),
    group: t("chatGroups"),
  }[kind] || accessKindLabel(kind);
}

function ensureAccessDraft() {
  if (state.accessDraft) return;
  state.accessDraft = {
    default_policy: JSON.parse(JSON.stringify(getByPath(state.config || {}, "access.default_policy") || defaultAccessItem("default_policy"))),
    identity: JSON.parse(JSON.stringify(getByPath(state.config || {}, "access.identities") || {})),
    user_group: JSON.parse(JSON.stringify(getByPath(state.config || {}, "access.user_groups") || {})),
    group: JSON.parse(JSON.stringify(getByPath(state.config || {}, "access.groups") || {})),
  };
  normalizeTemplateDrafts();
}

function normalizeTemplateDrafts() {
  ensureConfigDraft();
  for (const item of Object.values(state.accessDraft?.user_group || {})) {
    if (!item || typeof item !== "object") continue;
    item.preset_only = true;
    delete item.members;
    delete item.apply_to_all;
    delete item.permission_preset;
  }
  const templateKeys = Object.keys(state.accessDraft?.user_group || {});
  const current = templateKeyFromPreset(getByPath(state.configDraft, "access.default_template") || "");
  if ((!current || !templateKeys.includes(current)) && templateKeys.length) {
    setByPath(state.configDraft, "access.default_template", templateKeys[0]);
  }
}

function accessTargets() {
  ensureAccessDraft();
  const targets = [
    {
      id: "global:defaults",
      kind: "global",
      key: "defaults",
      item: {},
      label: `${t("globalDefaults")} + ${t("defaultPolicy")}`,
      haystack: `${t("defaultConfig")} ${t("globalDefaults")} ${t("defaultPolicy")} ${t("defaultTemplate")} global defaults default template config configuration`.toLowerCase(),
    },
  ];
  for (const kind of ["identity", "user_group", "group"]) {
    const collection = state.accessDraft[kind] || {};
    for (const [key, item] of Object.entries(collection)) {
      const haystack = [
        key,
        item.label,
        item.name,
        ...(item.aliases || []),
        ...(item.names || []),
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
  if (kind === "default_policy") {
    return { label: t("defaultPolicy"), allow_codex: false, unrestricted: false, tasks: [], skills: [], models: [], permission_preset: "inherit" };
  }
  if (kind === "identity") {
    return { label: "", open_ids: [], emails: [], names: [], aliases: [], allow_codex: false, unrestricted: false, tasks: [], skills: [], models: [] };
  }
  if (kind === "user_group") {
    return { label: "", enabled: true, preset_only: true, allow_codex: false, unrestricted: false, tasks: [], skills: [], models: [] };
  }
  return { label: "", enabled: true, members: [], allow_codex: false, unrestricted: false, tasks: [], skills: [], models: [] };
}

function currentTaskIds() {
  return Object.keys(getByPath(state.configDraft || state.config || {}, "preset_tasks") || {}).filter((item) => item !== "*");
}

function policyTaskIds(item = {}) {
  const ids = listValue(item.tasks).filter((value) => value !== "*" && value !== FREE_FORM_TASK_ID && value !== UNRESTRICTED_TASK_ID);
  return listValue(item.tasks).includes("*") ? currentTaskIds() : ids;
}

function accessTaskSelection(item = {}) {
  const values = listValue(item.tasks).filter((value) => value !== FREE_FORM_TASK_ID && value !== UNRESTRICTED_TASK_ID);
  if (item.allow_codex) values.push(FREE_FORM_TASK_ID);
  if (item.unrestricted) values.push(UNRESTRICTED_TASK_ID);
  return values;
}

function taskSubtaskIds(taskId, automaticOnly = false) {
  const task = getByPath(state.configDraft || state.config || {}, `preset_tasks.${taskId}`) || {};
  return normalizedTaskSubtasks(task.subtasks)
    .filter((item) => (automaticOnly ? item.type === "automatic" : item.type !== "automatic"))
    .map((item) => item.id)
    .filter(Boolean);
}

function subtaskOverrideChoice(field, taskId, currentMap, options) {
  const hasOverride = currentMap && Object.prototype.hasOwnProperty.call(currentMap, taskId);
  const values = new Set(hasOverride ? listValue(currentMap[taskId]) : options);
  const title = field === "auto_subtasks" ? t("autoSubtaskOverride") : t("manualSubtaskOverride");
  return `
    <div class="access-overrides-section">
      <h5>${escapeHtml(title)} · ${escapeHtml(taskId)}</h5>
      <label class="check"><input data-subtask-override-enabled="${escapeHtml(field)}" data-task-id="${escapeHtml(taskId)}" type="checkbox" ${hasOverride ? "checked" : ""} /><span>${escapeHtml(t("restrictToChecked"))}</span></label>
      <div class="choice-group" data-subtask-override="${escapeHtml(field)}" data-task-id="${escapeHtml(taskId)}">
        ${options
          .map(
            (id) => `
              <label class="chip-check">
                <input type="checkbox" value="${escapeHtml(id)}" ${values.has(id) ? "checked" : ""} />
                <span>${escapeHtml(id)}</span>
              </label>
            `,
          )
          .join("") || `<em>${escapeHtml(t("noExecutableTasks"))}</em>`}
      </div>
    </div>
  `;
}

function subtaskOverridesHtml(item = {}) {
  const taskIds = policyTaskIds(item);
  if (!taskIds.length) return "";
  const manualMap = item.task_subtasks && typeof item.task_subtasks === "object" ? item.task_subtasks : {};
  const autoMap = item.auto_subtasks && typeof item.auto_subtasks === "object" ? item.auto_subtasks : {};
  return `
    <details class="access-overrides" open>
      <summary>
        <span>${escapeHtml(t("subtaskOverrides"))}</span>
        <small>${escapeHtml(t("subtaskOverrides"))}</small>
      </summary>
      <div class="access-overrides-grid">
        ${taskIds.map((taskId) => subtaskOverrideChoice("task_subtasks", taskId, manualMap, taskSubtaskIds(taskId, false))).join("")}
        ${taskIds.map((taskId) => subtaskOverrideChoice("auto_subtasks", taskId, autoMap, taskSubtaskIds(taskId, true))).join("")}
      </div>
    </details>
  `;
}

function defaultModelPermissionIds() {
  const config = state.configDraft || state.config || {};
  const defaults = [
    getByPath(config, "models.default.model"),
    getByPath(config, "models.fast.model"),
  ].filter(Boolean);
  return defaults.length ? mergeOptionIds(defaults) : [];
}

function extractPolicyFields(item = {}) {
  const values = {};
  for (const field of POLICY_PERMISSION_FIELDS) {
    values[field] = Array.isArray(item[field]) ? [...item[field]] : item[field];
  }
  for (const field of POLICY_SUBTASK_FIELDS) {
    values[field] = item[field] && typeof item[field] === "object" && !Array.isArray(item[field]) ? cloneJson(item[field]) : {};
  }
  values.allow_codex = Boolean(values.allow_codex);
  values.unrestricted = Boolean(values.unrestricted);
  for (const field of ["tasks", "skills", "models"]) {
    values[field] = listValue(values[field]);
  }
  return values;
}

function cloneJson(value) {
  return JSON.parse(JSON.stringify(value ?? null));
}

function extractTemplateFields(item = {}) {
  const values = extractPolicyFields(item);
  values.settings = item.settings && typeof item.settings === "object" && !Array.isArray(item.settings) ? cloneJson(item.settings) : {};
  return values;
}

function normalizedTemplateFields(item = {}) {
  const values = extractTemplateFields(item);
  for (const field of ["tasks", "skills", "models"]) {
    values[field] = Array.from(new Set(values[field].map(String).filter(Boolean))).sort();
  }
  for (const field of POLICY_SUBTASK_FIELDS) {
    const map = values[field] && typeof values[field] === "object" && !Array.isArray(values[field]) ? values[field] : {};
    values[field] = Object.fromEntries(
      Object.entries(map)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, list]) => [key, Array.from(new Set(listValue(list).map(String).filter(Boolean))).sort()]),
    );
  }
  values.settings = pruneEmptyObject(values.settings || {}) || {};
  return values;
}

function templateFieldsEqual(left, right) {
  return JSON.stringify(normalizedTemplateFields(left)) === JSON.stringify(normalizedTemplateFields(right));
}

function templateKeyFromPreset(preset) {
  const value = String(preset || "");
  return value.startsWith("user_group:") ? value.slice("user_group:".length) : value;
}

function userGroupPolicyPresetEntries() {
  ensureAccessDraft();
  return Object.entries(state.accessDraft.user_group || {})
    .filter(([, item]) => item && item.enabled !== false)
    .map(([key, item]) => {
      const label = item.label || item.name || key;
      return {
        value: key,
        label: t("identityPresetOption", { label }),
        values: extractTemplateFields(item),
      };
    });
}

function policyPresetValues(preset) {
  ensureAccessDraft();
  const key = templateKeyFromPreset(preset);
  return extractTemplateFields(state.accessDraft.user_group?.[key] || {});
}

function policyPresetExists(preset) {
  const value = templateKeyFromPreset(preset);
  if (!value || value === "custom") return false;
  return userGroupPolicyPresetEntries().some((entry) => entry.value === value);
}

function detectedPolicyPreset(item = {}) {
  const savedPreset = templateKeyFromPreset(item.permission_preset || "");
  if (savedPreset) {
    return policyPresetExists(savedPreset) ? savedPreset : "custom";
  }
  const dynamicMatch = userGroupPolicyPresetEntries().find((entry) => templateFieldsEqual(item, entry.values));
  if (dynamicMatch) return dynamicMatch.value;
  return "custom";
}

function policyPresetOptionsHtml(selected) {
  const current = policyPresetExists(selected) ? templateKeyFromPreset(selected) : "custom";
  const customSelected = current === "custom" ? "selected" : "";
  const userGroups = userGroupPolicyPresetEntries()
    .map((entry) => `<option value="${escapeHtml(entry.value)}" ${entry.value === current ? "selected" : ""}>${escapeHtml(entry.label)}</option>`)
    .join("");
  return `<option value="custom" ${customSelected} disabled>${escapeHtml(t("presetCustom"))}</option>${userGroups}`;
}

function defaultTemplateOptionsHtml(selected) {
  const current = policyPresetExists(selected) ? templateKeyFromPreset(selected) : "";
  const templates = userGroupPolicyPresetEntries()
    .map((entry) => `<option value="${escapeHtml(entry.value)}" ${entry.value === current ? "selected" : ""}>${escapeHtml(entry.label)}</option>`)
    .join("");
  return templates || `<option value="">${escapeHtml(t("noAccessMatches"))}</option>`;
}

function renderDefaultTemplateSelectOptions() {
  const select = document.querySelector("[data-default-template-select]");
  if (!select) return;
  const value = getByPath(state.configDraft || state.config || {}, "access.default_template") || "";
  select.innerHTML = defaultTemplateOptionsHtml(value);
  if (policyPresetExists(value)) select.value = templateKeyFromPreset(value);
}

function defaultPolicyFromTemplate() {
  const template = getByPath(state.configDraft || state.config || {}, "access.default_template") || "";
  if (policyPresetExists(template)) {
    const values = policyPresetValues(template);
    return cloneJson(values);
  }
  return state.accessDraft?.default_policy || defaultAccessItem("default_policy");
}

function applyPolicyPreset(item, preset) {
  const next = { ...item };
  const values = policyPresetValues(preset);
  for (const key of TEMPLATE_CONFIG_FIELDS) {
    if (key === "settings") {
      if (values.settings && Object.keys(values.settings).length) next.settings = cloneJson(values.settings);
      else delete next.settings;
    } else {
      next[key] = Array.isArray(values[key]) ? [...values[key]] : values[key];
    }
  }
  const key = templateKeyFromPreset(preset);
  if (policyPresetExists(key)) {
    next.permission_preset = key;
  } else {
    delete next.permission_preset;
  }
  return next;
}

function syncItemWithPermissionPreset(item) {
  const preset = String(item?.permission_preset || "");
  if (!preset) return false;
  if (!policyPresetExists(preset)) {
    delete item.permission_preset;
    return true;
  }
  const next = applyPolicyPreset(item, preset);
  let changed = false;
  for (const key of TEMPLATE_CONFIG_FIELDS.concat("permission_preset")) {
    if (JSON.stringify(item[key]) !== JSON.stringify(next[key])) {
      if (next[key] === undefined) delete item[key];
      else item[key] = Array.isArray(next[key]) ? [...next[key]] : cloneJson(next[key]);
      changed = true;
    }
  }
  return changed;
}

function syncPresetBackedPolicies() {
  ensureAccessDraft();
  let changed = false;
  for (const kind of ["identity", "group"]) {
    for (const item of Object.values(state.accessDraft[kind] || {})) {
      if (item && syncItemWithPermissionPreset(item)) changed = true;
    }
  }
  return changed;
}

function updatePermissionPresetReferences(oldPreset, newPreset) {
  if (!oldPreset || oldPreset === newPreset) return false;
  let changed = false;
  const updateItem = (item) => {
    const current = templateKeyFromPreset(item?.permission_preset || "");
    if (current === oldPreset || current === templateKeyFromPreset(oldPreset)) {
      item.permission_preset = newPreset;
      changed = true;
    }
  };
  updateItem(state.accessDraft.default_policy);
  for (const kind of ["identity", "group"]) {
    for (const item of Object.values(state.accessDraft[kind] || {})) {
      updateItem(item);
    }
  }
  const draft = ensureConfigDraft();
  if (templateKeyFromPreset(getByPath(draft, "access.default_template") || "") === templateKeyFromPreset(oldPreset)) {
    setByPath(draft, "access.default_template", newPreset);
    changed = true;
  }
  return changed;
}

function reasoningOptions(name) {
  return `
    <select name="${name}">
      <option value="">config</option>
      <option value="low">low</option>
      <option value="medium">medium</option>
      <option value="high">high</option>
      <option value="xhigh">xhigh</option>
    </select>
  `;
}

function serviceTierOptions(name) {
  return `<select name="${name}" data-service-tier-select></select>`;
}

function globalConfigCard() {
  return `
    <article class="config-global-card" data-config-target-kind="global">
      <h4>${escapeHtml(t("globalDefaults"))}</h4>
      <details class="config-group" open>
        <summary><span>${escapeHtml(t("assistantPrivacyGroup"))}</span><small>${escapeHtml(t("assistantPrivacyHint"))}</small></summary>
        <div class="config-group-grid">
          <label><span>${escapeHtml(t("assistantDisplayName"))}</span><input name="assistant.display_name" type="text" autocomplete="off" /></label>
          <label class="check"><input name="assistant.hide_internal_identity" type="checkbox" /><span>${escapeHtml(t("hideInternalIdentity"))}</span></label>
          <label><span>${escapeHtml(t("replyMaxChars"))}</span><input name="reply.max_chars" type="number" min="500" step="100" /></label>
          <label class="wide"><span>${escapeHtml(t("assistantIdentityPrompt"))}</span><textarea name="assistant.identity_prompt" rows="3"></textarea></label>
        </div>
      </details>
      <details class="config-group" open>
        <summary><span>${escapeHtml(t("defaultPolicy"))}</span><small>${escapeHtml(t("settingsOverridesHint"))}</small></summary>
        <div class="config-group-grid">
          <label>
            <span>${escapeHtml(t("defaultTemplate"))}</span>
            <select name="access.default_template" data-default-template-select></select>
          </label>
        </div>
      </details>
      <details class="config-group" open>
        <summary><span>${escapeHtml(t("modelGroup"))}</span><small>${escapeHtml(t("modelGroupHint"))}</small></summary>
        <div class="config-group-grid">
          <label><span>${escapeHtml(t("defaultModel"))}</span><select name="models.default.model" data-model-select></select></label>
          <label><span>${escapeHtml(t("defaultReasoning"))}</span>${reasoningOptions("models.default.reasoning_effort")}</label>
          <label><span>${escapeHtml(t("defaultTier"))}</span>${serviceTierOptions("models.default.service_tier")}</label>
          <label><span>${escapeHtml(t("fastModel"))}</span><select name="models.fast.model" data-model-select></select></label>
          <label><span>${escapeHtml(t("fastReasoning"))}</span>${reasoningOptions("models.fast.reasoning_effort")}</label>
          <label><span>${escapeHtml(t("fastTier"))}</span>${serviceTierOptions("models.fast.service_tier")}</label>
        </div>
      </details>
      <details class="config-group">
        <summary><span>${escapeHtml(t("runtimeGroup"))}</span><small>${escapeHtml(t("runtimeGroupHint"))}</small></summary>
        <div class="config-group-grid">
          <label class="wide"><span>${escapeHtml(t("codexHomeDir"))}</span><input name="codex.home_dir" type="text" autocomplete="off" placeholder="Default local .codex" /></label>
          <label>
            <span>${escapeHtml(t("sandbox"))}</span>
            <select name="private.codex_sandbox">
              <option value="workspace-write">workspace-write</option>
              <option value="read-only">read-only</option>
              <option value="danger-full-access">danger-full-access</option>
            </select>
          </label>
          <label><span>${escapeHtml(t("timeoutSeconds"))}</span><input name="private.codex_timeout_sec" type="number" min="60" step="30" /></label>
          <label><span>${escapeHtml(t("activeOutputGrace"))}</span><input name="private.codex_active_output_grace_sec" type="number" min="0" step="30" /></label>
          <label><span>${escapeHtml(t("timeoutExtension"))}</span><input name="private.codex_timeout_extension_sec" type="number" min="0" step="30" /></label>
          <label><span>${escapeHtml(t("finalOutputReady"))}</span><input name="private.final_output_ready_sec" type="number" min="1" step="1" /></label>
          <label><span>${escapeHtml(t("finalOutputIdle"))}</span><input name="private.final_output_idle_grace_sec" type="number" min="5" step="5" /></label>
          <label><span>${escapeHtml(t("maxConcurrentJobs"))}</span><input name="jobs.max_concurrent" type="number" min="1" max="8" /></label>
          <label><span>${escapeHtml(t("jobHistoryLimit"))}</span><input name="jobs.history_limit" type="number" min="1" max="1000" /></label>
          <label class="check"><input name="jobs.auto_cleanup_enabled" type="checkbox" /><span>${escapeHtml(t("autoCleanupJobs"))}</span></label>
          <label class="check"><input name="jobs.cleanup_delete_artifacts" type="checkbox" /><span>${escapeHtml(t("deleteJobArtifacts"))}</span></label>
        </div>
      </details>
      <details class="config-group" open>
        <summary><span>${escapeHtml(t("conversationReplyGroup"))}</span><small>${escapeHtml(t("conversationReplyHint"))}</small></summary>
        <div class="config-group-grid">
          <label class="check"><input name="sessions.enabled" type="checkbox" /><span>${escapeHtml(t("sessionsEnabled"))}</span></label>
          <label>
            <span>${escapeHtml(t("sessionMode"))}</span>
            <select name="sessions.mode">
              <option value="continuous">${escapeHtml(t("sessionModeContinuous"))}</option>
              <option value="topic">${escapeHtml(t("sessionModeTopic"))}</option>
            </select>
          </label>
          <label class="check"><input name="sessions.topic_reply_in_thread" type="checkbox" /><span>${escapeHtml(t("topicReplyInThread"))}</span></label>
          <label class="check"><input name="sessions.queue_while_running" type="checkbox" /><span>${escapeHtml(t("queueWhileRunning"))}</span></label>
          <label class="check"><input name="reply.edit_status_message" type="checkbox" /><span>${escapeHtml(t("editStatusMessage"))}</span></label>
          <label class="check"><input name="reply.show_details_by_default" type="checkbox" /><span>${escapeHtml(t("showDetailsByDefault"))}</span></label>
          <label class="check"><input name="reply.show_progress_by_default" type="checkbox" /><span>${escapeHtml(t("showProgressByDefault"))}</span></label>
          <label><span>${escapeHtml(t("progressMaxLines"))}</span><input name="reply.progress_max_lines" type="number" min="1" max="20" step="1" /></label>
          <label><span>${escapeHtml(t("statusInterval"))}</span><input name="reply.status_update_interval_sec" type="number" min="3" step="1" /></label>
        </div>
      </details>
      <details class="config-group" open>
        <summary><span>${escapeHtml(t("responseTargetGroup"))}</span><small>${escapeHtml(t("responseTargetHint"))}</small></summary>
        <div class="config-group-grid response-target-grid">
          <label class="check"><input name="routing.accept_any_target" type="checkbox" /><span>${escapeHtml(t("acceptAny"))}</span></label>
          <label class="check"><input name="routing.only_respond_to_bot_mention" type="checkbox" /><span>${escapeHtml(t("onlyRespondToBot"))}</span></label>
          <label class="check"><input name="routing.private_only_respond_to_bot_mention" type="checkbox" /><span>${escapeHtml(t("privateOnlyRespondToBot"))}</span></label>
        </div>
      </details>
      <details class="config-group">
        <summary><span>${escapeHtml(t("routingGroup"))}</span><small>${escapeHtml(t("routingGroupHint"))}</small></summary>
        <div class="config-group-grid">
          <label class="check"><input name="public.allow_codex" type="checkbox" /><span>${escapeHtml(t("allowGroupCodex"))}</span></label>
          <label class="check"><input name="public.treat_all_text_as_codex" type="checkbox" /><span>${escapeHtml(t("groupPlainText"))}</span></label>
          <label class="check"><input name="private.treat_all_text_as_codex" type="checkbox" /><span>${escapeHtml(t("privatePlainText"))}</span></label>
          <label class="check"><input name="private.polling_fallback_enabled" type="checkbox" /><span>${escapeHtml(t("privatePollingFallback"))}</span></label>
          <label class="check"><input name="multimodal.download_incoming" type="checkbox" /><span>${escapeHtml(t("downloadIncomingMedia"))}</span></label>
          <label class="check"><input name="routing.dispatch_to_peers" type="checkbox" /><span>${escapeHtml(t("dispatchToPeers"))}</span></label>
          <label class="check"><input name="access.enable_preset_intent_matching" type="checkbox" /><span>${escapeHtml(t("matchPresetAliases"))}</span></label>
          <label class="check"><input name="access.resolve_contacts_enabled" type="checkbox" /><span>${escapeHtml(t("resolveContacts"))}</span></label>
          <label><span>${escapeHtml(t("contactCacheTtl"))}</span><input name="access.contact_cache_ttl_sec" type="number" min="60" step="60" /></label>
        </div>
      </details>
      <details class="config-group">
        <summary><span>${escapeHtml(t("detectedRuntimeGroup"))}</span><small>${escapeHtml(t("detectedRuntimeHint"))}</small></summary>
        <div class="runtime-options-wrap">
          <div id="detectedSkills" class="detected-options"></div>
          <div id="detectedModels" class="detected-options"></div>
        </div>
      </details>
      <section class="preset-task-editor" id="presetTaskEditor"></section>
      <section class="scheduled-task-editor" id="scheduledTaskEditor"></section>
      <label class="wide global-json-editor preset-task-json">
        <span>${escapeHtml(t("presetTasksJson"))}</span>
        <textarea name="preset_tasks" data-json="object" rows="8"></textarea>
      </label>
      <label class="wide global-json-editor preset-task-json">
        <span>${escapeHtml(t("scheduledTasks"))}</span>
        <textarea name="task_scheduler" data-json="object" rows="8"></textarea>
      </label>
    </article>
  `;
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
  const isDefaultPolicy = kind === "default_policy";
  const isChatGroup = kind === "group";
  const isIdentity = kind === "identity";
  const isUserGroup = kind === "user_group";
  const canApplyPermissionPreset = isIdentity || isChatGroup;
  const currentPermissionPreset = canApplyPermissionPreset ? detectedPolicyPreset(item) : "";
  const fieldKey = isIdentity ? "userKey" : isChatGroup ? "groupKey" : "userGroupKey";
  const listLabel = isIdentity ? "openIds" : isChatGroup ? "chatIds" : "members";
  const listField = isIdentity ? "open_ids" : isChatGroup ? "chat_ids" : "members";
  const identityOrGroupFields =
    !isDefaultPolicy && !isUserGroup
      ? `
        <div class="access-card-grid">
          <label>
            <span>${escapeHtml(t(listLabel))}</span>
            <textarea data-access-list="${escapeHtml(listField)}" rows="3">${escapeFormValue(listValue(item[listField]).join("\n"))}</textarea>
          </label>
          ${
            isIdentity
              ? `<label><span>${escapeHtml(t("emails"))}</span><textarea data-access-list="emails" rows="3">${escapeFormValue(listValue(item.emails).join("\n"))}</textarea></label>`
              : `<label><span>${escapeHtml(t("searchAliases"))}</span><textarea data-access-list="aliases" rows="3">${escapeFormValue(listValue(item.aliases).join("\n"))}</textarea></label>`
          }
          ${
            isIdentity
              ? `<label><span>${escapeHtml(t("names"))}</span><textarea data-access-list="names" rows="3">${escapeFormValue(listValue(item.names).join("\n"))}</textarea></label><label><span>${escapeHtml(t("aliases"))}</span><textarea data-access-list="aliases" rows="3">${escapeFormValue(listValue(item.aliases).join("\n"))}</textarea></label>`
              : ""
          }
        </div>
      `
      : "";
  return `
    <article class="access-card" data-access-kind="${escapeHtml(kind)}" data-original-key="${escapeHtml(key)}">
      <div class="access-card-toolbar">
        <strong>${escapeHtml(isDefaultPolicy ? t("permissionDefaults") : accessKindLabel(kind))}</strong>
        <div class="access-card-actions">
          ${
            canApplyPermissionPreset
              ? `
                <label>
                  <span>${escapeHtml(t("permissionPreset"))}</span>
                  <select data-policy-preset>${policyPresetOptionsHtml(currentPermissionPreset)}</select>
                </label>
              `
              : isUserGroup
                ? `<span class="access-preset-note">${escapeHtml(t("identityPresetNote"))}</span>`
                : ""
          }
          ${isDefaultPolicy ? "" : `<button type="button" class="secondary danger" data-delete-access>${escapeHtml(t("deleteAccessTarget"))}</button>`}
        </div>
      </div>
      ${
        isDefaultPolicy
          ? ""
          : `
            <div class="access-card-head">
              <label>
                <span>${escapeHtml(t(fieldKey))}</span>
                <input data-access-field="key" value="${escapeHtml(key)}" />
              </label>
              <label>
                <span>${escapeHtml(t("label"))}</span>
                <input data-access-field="label" value="${escapeFormValue(item.label || item.name || "")}" />
              </label>
            </div>
            ${identityOrGroupFields}
          `
      }
      <div class="access-toggles">
        ${
          !isIdentity && !isDefaultPolicy
            ? `<label class="check"><input data-access-bool="enabled" type="checkbox" ${item.enabled === false ? "" : "checked"} /><span>${escapeHtml(t("enabled"))}</span></label>`
            : ""
        }
      </div>
      <p class="access-mode-hint">${escapeHtml(t("accessModeHint"))}</p>
      <div class="access-permissions">
        <section>
          <strong>${escapeHtml(t("tasks"))}</strong>
          <small>${escapeHtml(t("taskPermissionHint"))}</small>
          ${choiceGroup("tasks", accessTaskSelection(item), optionIds("tasks"))}
        </section>
        <section>
          <strong>${escapeHtml(t("models"))}</strong>
          <small>${escapeHtml(t("freeTaskLimitHint"))}</small>
          ${choiceGroup("models", item.models, optionIds("models"))}
        </section>
        <section>
          <strong>${escapeHtml(t("skills"))}</strong>
          <small>${escapeHtml(t("freeTaskLimitHint"))}</small>
          ${choiceGroup("skills", item.skills, optionIds("skills"))}
        </section>
      </div>
      ${subtaskOverridesHtml(item)}
      <div class="access-settings-grid">
        <section class="access-overrides-section">
          <h5>${escapeHtml(t("assistantOverrides"))}</h5>
          ${accessTextSetting("assistant.display_name", item, "assistantDisplayName")}
          ${accessBoolSetting("assistant.hide_internal_identity", item, "hideInternalIdentity")}
          ${accessTextSetting("assistant.identity_prompt", item, "assistantIdentityPrompt", 3)}
        </section>
        <section class="access-overrides-section">
          <h5>${escapeHtml(t("modelOverrides"))}</h5>
          ${accessSelectSetting("models.default.model", item, "defaultModel", modelIdsFromConfig())}
          ${accessSelectSetting("models.default.reasoning_effort", item, "defaultReasoning", ["low", "medium", "high", "xhigh"])}
          ${accessSelectSetting("models.default.service_tier", item, "defaultTier", serviceTierIdsFromConfig())}
          ${accessSelectSetting("models.fast.model", item, "fastModel", modelIdsFromConfig())}
          ${accessSelectSetting("models.fast.reasoning_effort", item, "fastReasoning", ["low", "medium", "high", "xhigh"])}
          ${accessSelectSetting("models.fast.service_tier", item, "fastTier", serviceTierIdsFromConfig())}
        </section>
        <section class="access-overrides-section">
          <h5>${escapeHtml(t("conversationReplyGroup"))}</h5>
          ${accessBoolSetting("sessions.enabled", item, "sessionsEnabled")}
          ${accessSelectSetting("sessions.mode", item, "sessionMode", ["continuous", "topic"])}
          ${accessBoolSetting("sessions.topic_reply_in_thread", item, "topicReplyInThread")}
          ${accessBoolSetting("sessions.queue_while_running", item, "queueWhileRunning")}
        </section>
        <section class="access-overrides-section">
          <h5>${escapeHtml(t("runtimeOverrides"))}</h5>
          ${accessSelectSetting("private.default_workspace", item, "defaultWorkspace", workspaceIdsFromConfig())}
          ${accessSelectSetting("private.codex_sandbox", item, "sandbox", ["workspace-write", "read-only", "danger-full-access"])}
          ${accessNumberSetting("private.codex_timeout_sec", item, "timeoutSeconds", 'min="60" step="30"')}
          ${accessNumberSetting("private.codex_active_output_grace_sec", item, "activeOutputGrace", 'min="0" step="30"')}
          ${accessNumberSetting("private.codex_timeout_extension_sec", item, "timeoutExtension", 'min="0" step="30"')}
          ${accessNumberSetting("private.final_output_ready_sec", item, "finalOutputReady", 'min="1" step="1"')}
          ${accessNumberSetting("private.final_output_idle_grace_sec", item, "finalOutputIdle", 'min="5" step="5"')}
        </section>
        <section class="access-overrides-section">
          <h5>${escapeHtml(t("replyOverrides"))}</h5>
          ${accessBoolSetting("reply.edit_status_message", item, "editStatusMessage")}
          ${accessBoolSetting("reply.show_details", item, "showDetails")}
          ${accessBoolSetting("reply.show_progress", item, "showProgress")}
          ${accessNumberSetting("reply.max_chars", item, "replyMaxChars", 'min="500" step="100"')}
          ${accessNumberSetting("reply.progress_max_lines", item, "progressMaxLines", 'min="1" max="20" step="1"')}
          ${accessNumberSetting("reply.status_update_interval_sec", item, "statusInterval", 'min="3" step="1"')}
        </section>
        <section class="access-overrides-section">
          <h5>${escapeHtml(t("routingGroup"))}</h5>
          ${accessBoolSetting("routing.accept_any_target", item, "acceptAny")}
          ${accessBoolSetting("routing.only_respond_to_bot_mention", item, "onlyRespondToBot")}
          ${accessBoolSetting("routing.private_only_respond_to_bot_mention", item, "privateOnlyRespondToBot")}
          ${accessBoolSetting("public.treat_all_text_as_codex", item, "groupPlainText")}
          ${accessBoolSetting("private.treat_all_text_as_codex", item, "privatePlainText")}
          ${accessBoolSetting("multimodal.download_incoming", item, "downloadIncomingMedia")}
          ${accessBoolSetting("access.enable_preset_intent_matching", item, "matchPresetAliases")}
        </section>
      </div>
    </article>
  `;
}

function defaultConfigCard(defaultPolicy) {
  return `
    <div class="default-config-stack">
      ${globalConfigCard()}
    </div>
  `;
}

function normalizedAccessSearch(value) {
  return String(value || "").trim() === "-" ? "" : String(value || "");
}

function accessTargetListHtml(filtered, selected) {
  if (!filtered.length) return `<p class="empty-copy">${escapeHtml(t("noAccessMatches"))}</p>`;
  const searchActive = Boolean(normalizedAccessSearch(state.accessSearch));
  return ["global", "user_group", "identity", "group"]
    .map((groupKind) => {
      const items = filtered.filter((target) => accessGroupKind(target.kind) === groupKind);
      if (!items.length) return "";
      const selectedInGroup = items.some((target) => target.id === selected?.id);
      const open = searchActive || selectedInGroup || state.accessGroupsOpen[groupKind] !== false;
      return `
        <details class="access-target-group" data-access-group="${escapeHtml(groupKind)}" ${open ? "open" : ""}>
          <summary>
            <span>${escapeHtml(accessGroupLabel(groupKind))}</span>
            <small>${items.length}</small>
          </summary>
          <div class="access-target-group-list">
            ${items
              .map((target) => {
                const preset = target.item?.permission_preset ? `<span>${escapeHtml(t("syncedPermissionPreset"))}</span>` : "";
                const templateOnly = target.item?.preset_only ? `<span>${escapeHtml(t("templateOnly"))}</span>` : "";
                return `
                  <button type="button" class="access-target ${target.id === selected?.id ? "active" : ""}" data-access-target="${escapeHtml(target.id)}">
                    <span>${escapeHtml(accessKindLabel(target.kind))}</span>
                    <strong>${escapeHtml(target.label)}</strong>
                    <code>${escapeHtml(target.key)}</code>
                    ${preset}
                    ${templateOnly}
                  </button>
                `;
              })
              .join("")}
          </div>
        </details>
      `;
    })
    .join("");
}

function filteredAccessTargets() {
  const targets = accessTargets();
  const search = normalizedAccessSearch(state.accessSearch);
  return {
    targets,
    filtered: search ? targets.filter((target) => target.haystack.includes(search.trim().toLowerCase())) : targets,
    selected: selectedAccessTarget(),
    search,
  };
}

function bindAccessTargetButtons() {
  document.querySelectorAll("[data-access-group]").forEach((group) => {
    group.addEventListener("toggle", () => {
      if (normalizedAccessSearch(state.accessSearch)) return;
      state.accessGroupsOpen[group.dataset.accessGroup] = group.open;
    });
  });
  document.querySelectorAll("[data-access-target]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      syncGlobalConfigDraft();
      syncAccessDetail();
      if (syncPresetBackedPolicies()) markAccessEditing();
      state.selectedAccessTarget = button.dataset.accessTarget;
      renderAccessEditor({ skipSync: true });
    });
  });
}

function deleteSelectedAccessTarget() {
  ensureAccessDraft();
  const card = document.querySelector("#configTargetDetail [data-access-kind]");
  if (!card) return;
  const kind = card.dataset.accessKind;
  if (kind === "default_policy") return;
  const originalKey = card.dataset.originalKey;
  const currentKey = card.querySelector('[data-access-field="key"]')?.value.trim();
  if (!kind || !state.accessDraft[kind]) return;
  if (originalKey) delete state.accessDraft[kind][originalKey];
  if (currentKey) delete state.accessDraft[kind][currentKey];
  if (kind === "user_group") {
    normalizeTemplateDrafts();
    syncPresetBackedPolicies();
  }
  state.selectedAccessTarget = "";
  markAccessEditing();
  renderAccessEditor({ skipSync: true });
}

function renderAccessTargetList() {
  const list = $("#configTargetList");
  if (!list) return;
  const { filtered, selected } = filteredAccessTargets();
  list.innerHTML = accessTargetListHtml(filtered, selected);
  bindAccessTargetButtons();
}

function renderAccessEditor(options = {}) {
  const targetList = $("#configTargetList");
  const detail = $("#configTargetDetail");
  if (!targetList || !detail) return;
  if (state.accessDraft && !options.skipSync) {
    syncGlobalConfigDraft();
    syncAccessDetail();
  }
  ensureAccessDraft();
  let search = normalizedAccessSearch(state.accessSearch);
  if (document.activeElement?.id === "configTargetSearch") {
    search = normalizedAccessSearch($("#configTargetSearch")?.value || "");
  }
  state.accessSearch = search;
  const { filtered, selected } = filteredAccessTargets();
  targetList.innerHTML = accessTargetListHtml(filtered, selected);
  detail.innerHTML = selected
    ? selected.kind === "global"
      ? defaultConfigCard(state.accessDraft.default_policy || defaultAccessItem("default_policy"))
      : `<h4>${escapeHtml(t("accessTarget"))}: ${escapeHtml(accessKindLabel(selected.kind))}</h4>${accessCard(selected.kind, selected.key, selected.item)}`
    : `<p class="empty-copy">${escapeHtml(t("noAccessMatches"))}</p>`;

  const searchInput = $("#configTargetSearch");
  if (searchInput && searchInput.value !== search) searchInput.value = search;
  if (searchInput) searchInput.oninput = (event) => {
    const value = normalizedAccessSearch(event.target.value);
    state.accessSearch = value;
    if (event.target.value !== value) event.target.value = value;
    renderAccessTargetList();
  };
  if (options.focusSearch && searchInput) {
    searchInput.focus();
    searchInput.setSelectionRange(searchInput.value.length, searchInput.value.length);
  }
  bindAccessTargetButtons();
  detail.querySelector("[data-delete-access]")?.addEventListener("click", (event) => {
    event.preventDefault();
    deleteSelectedAccessTarget();
  });
  detail.querySelector("[data-policy-preset]")?.addEventListener("change", (event) => {
    event.preventDefault();
    applySelectedPolicyPreset();
  });
  detail.querySelector('[data-choice-field="tasks"]')?.addEventListener("change", () => {
    syncAccessDetail();
    markAccessEditing();
    renderAccessEditor({ skipSync: true });
  });
  renderModelSelectOptions(state.configDraft || state.config || {});
  renderServiceTierSelectOptions(state.configDraft || state.config || {});
  renderDefaultTemplateSelectOptions();
  populateGlobalConfigFields();
  renderPresetTaskEditor();
  renderScheduledTaskEditor();
  renderRuntimeOptionsPreview();
  applyOptionHelp();
  setConfigControlsWritable(state.lastConfigPayload ? Boolean(state.lastConfigPayload.allow_config_write) : true);
}

function syncAccessDetail() {
  ensureAccessDraft();
  const card = document.querySelector("#configTargetDetail [data-access-kind]");
  if (!card) return;
  const kind = card.dataset.accessKind;
  const keepGlobalSelected = state.selectedAccessTarget === "global:defaults";
  const originalKey = card.dataset.originalKey;
  const key = kind === "default_policy" ? "default" : card.querySelector('[data-access-field="key"]')?.value.trim();
  if (!kind || !originalKey || !key) return;
  const existingItem =
    kind === "default_policy"
      ? state.accessDraft.default_policy || {}
      : state.accessDraft[kind]?.[originalKey] || state.accessDraft[kind]?.[key] || {};
  const item = JSON.parse(JSON.stringify(existingItem || {}));
  card.querySelectorAll("[data-access-field]").forEach((field) => {
    const name = field.dataset.accessField;
    if (name === "key") return;
    const value = field.value.trim();
    if (value) {
      item[name] = value;
    } else {
      delete item[name];
    }
  });
  card.querySelectorAll("[data-access-list]").forEach((field) => {
    item[field.dataset.accessList] = splitLines(field.value);
  });
  card.querySelectorAll("[data-access-bool]").forEach((field) => {
    item[field.dataset.accessBool] = Boolean(field.checked);
  });
  card.querySelectorAll("[data-choice-field]").forEach((group) => {
    const values = Array.from(group.querySelectorAll("input:checked")).map((input) => input.value);
    if (group.dataset.choiceField === "tasks") {
      item.allow_codex = values.includes(FREE_FORM_TASK_ID) || values.includes(UNRESTRICTED_TASK_ID);
      item.unrestricted = values.includes(UNRESTRICTED_TASK_ID);
      item.tasks = values.filter((value) => value !== FREE_FORM_TASK_ID && value !== UNRESTRICTED_TASK_ID);
    } else {
      item[group.dataset.choiceField] = values;
    }
  });
  delete item.commands;
  const subtaskMaps = { task_subtasks: {}, auto_subtasks: {} };
  card.querySelectorAll("[data-subtask-override]").forEach((group) => {
    const field = group.dataset.subtaskOverride;
    const taskId = group.dataset.taskId;
    const enabled = card.querySelector(`[data-subtask-override-enabled="${CSS.escape(field)}"][data-task-id="${CSS.escape(taskId)}"]`)?.checked;
    if (!enabled || !subtaskMaps[field]) return;
    subtaskMaps[field][taskId] = Array.from(group.querySelectorAll("input:checked")).map((input) => input.value);
  });
  for (const field of POLICY_SUBTASK_FIELDS) {
    if (Object.keys(subtaskMaps[field]).length) item[field] = subtaskMaps[field];
    else delete item[field];
  }
  if (kind === "user_group") {
    item.preset_only = true;
    delete item.members;
    delete item.apply_to_all;
    delete item.permission_preset;
  }
  const settings = {};
  card.querySelectorAll("[data-access-setting]").forEach((field) => {
    const value = String(field.value || "").trim();
    if (!value) return;
    if (field.type === "number") {
      const numeric = Number(value);
      if (Number.isFinite(numeric)) setByPath(settings, field.dataset.accessSetting, numeric);
      return;
    }
    setByPath(settings, field.dataset.accessSetting, value);
  });
  card.querySelectorAll("[data-access-setting-bool]").forEach((field) => {
    const value = String(field.value || "");
    if (value === "true" || value === "false") {
      setByPath(settings, field.dataset.accessSettingBool, value === "true");
    }
  });
  const cleanedSettings = pruneEmptyObject(settings);
  delete item.show_details;
  delete item.show_progress;
  if (Object.keys(cleanedSettings).length) {
    item.settings = cleanedSettings;
  } else {
    delete item.settings;
  }
  const preset = card.querySelector("[data-policy-preset]")?.value || "";
  if (preset && preset !== "custom" && policyPresetExists(preset) && templateFieldsEqual(item, policyPresetValues(preset))) {
    item.permission_preset = templateKeyFromPreset(preset);
  } else {
    delete item.permission_preset;
  }
  if (kind === "default_policy") {
    state.accessDraft.default_policy = item;
    state.selectedAccessTarget = keepGlobalSelected ? "global:defaults" : "default_policy:default";
    return;
  }
  if (!state.accessDraft[kind]) state.accessDraft[kind] = {};
  if (originalKey !== key) {
    delete state.accessDraft[kind][originalKey];
  }
  state.accessDraft[kind][key] = item;
  if (kind === "user_group" && originalKey !== key) {
    updatePermissionPresetReferences(originalKey, key);
  }
  state.selectedAccessTarget = `${kind}:${key}`;
}

function readConfigElementValue(element) {
  if (element.type === "checkbox") {
    return element.checked;
  }
  if (element.type === "number") {
    return Number(element.value);
  }
  if (element.dataset.json === "array") {
    const raw = element.value.trim();
    return raw.startsWith("[")
      ? JSON.parse(raw || "[]")
      : raw
          .split(/\r?\n|,/)
          .map((item) => item.trim())
          .filter(Boolean);
  }
  if (element.dataset.json === "object") {
    return JSON.parse(element.value || "{}");
  }
  return element.value;
}

function syncGlobalConfigDraft() {
  const form = $("#configForm");
  if (!form) return;
  ensureConfigDraft();
  syncPresetTaskDetail();
  syncScheduledTaskDetail();
  for (const element of form.elements) {
    if (!element.name) continue;
    setByPath(state.configDraft, element.name, readConfigElementValue(element));
  }
}

function populateGlobalConfigFields() {
  const source = state.configDraft || state.config || {};
  for (const field of GLOBAL_CONFIG_FIELDS) {
    let value = getByPath(source, field);
    if (field === "sessions.mode") value = value || "continuous";
    if (field === "sessions.topic_reply_in_thread" && value === undefined) value = true;
    if (field === "assistant.hide_internal_identity" && value === undefined) value = true;
    setByName(field, value);
  }
}

function selectedAccessDraftItem() {
  ensureAccessDraft();
  const [kind, key] = String(state.selectedAccessTarget || "default_policy:default").split(":");
  if (kind === "global") return { kind: "default_policy", key: "default", item: state.accessDraft.default_policy || defaultAccessItem("default_policy") };
  if (kind === "default_policy") return { kind, key: "default", item: state.accessDraft.default_policy || defaultAccessItem("default_policy") };
  return { kind, key, item: state.accessDraft[kind]?.[key] };
}

function applySelectedPolicyPreset() {
  ensureAccessDraft();
  const keepGlobalSelected = state.selectedAccessTarget === "global:defaults";
  syncAccessDetail();
  const preset = document.querySelector("[data-policy-preset]")?.value || "inherit";
  if (preset === "custom") return;
  const selected = selectedAccessDraftItem();
  if (!selected.item) return;
  const next = applyPolicyPreset(selected.item, preset);
  if (selected.kind === "default_policy") {
    state.accessDraft.default_policy = next;
    state.selectedAccessTarget = keepGlobalSelected ? "global:defaults" : "default_policy:default";
  } else {
    state.accessDraft[selected.kind][selected.key] = next;
    state.selectedAccessTarget = `${selected.kind}:${selected.key}`;
  }
  markAccessEditing();
  renderAccessEditor({ skipSync: true });
}

function addAccessCard(kind) {
  ensureAccessDraft();
  syncAccessDetail();
  markAccessEditing();
  const prefix = kind === "group" ? "chat" : kind === "user_group" ? "template" : "user";
  const key = `${prefix}-${Date.now()}`;
  if (!state.accessDraft[kind]) state.accessDraft[kind] = {};
  state.accessDraft[kind][key] = defaultAccessItem(kind);
  if (kind === "user_group" && !getByPath(ensureConfigDraft(), "access.default_template")) {
    setByPath(state.configDraft, "access.default_template", key);
  }
  state.selectedAccessTarget = `${kind}:${key}`;
  renderAccessEditor({ skipSync: true });
}

function stableAccessKey(prefix, id) {
  const raw = String(id || "").replace(/[^A-Za-z0-9_-]/g, "");
  const suffix = raw.slice(-12) || String(Date.now());
  return `${prefix}-${suffix}`;
}

function uniqueAccessKey(collection, preferred) {
  if (!collection[preferred]) return preferred;
  let index = 2;
  while (collection[`${preferred}-${index}`]) index += 1;
  return `${preferred}-${index}`;
}

function findIdentityByOpenId(openId) {
  const target = String(openId || "");
  if (!target) return "";
  for (const [key, item] of Object.entries(state.accessDraft?.identity || {})) {
    if (listValue(item.open_ids).includes(target)) return key;
  }
  return "";
}

function findGroupByChatId(chatId) {
  const target = String(chatId || "");
  if (!target) return "";
  for (const [key, item] of Object.entries(state.accessDraft?.group || {})) {
    if (listValue(item.chat_ids).includes(target)) return key;
  }
  return "";
}

function defaultTemplateForDiscovery() {
  const configured = getByPath(state.configDraft || state.config || {}, "access.default_template") || "";
  if (policyPresetExists(configured)) return templateKeyFromPreset(configured);
  if (policyPresetExists("no-access")) return "no-access";
  return "";
}

function defaultDiscoveredAccessItem(kind) {
  const preset = defaultTemplateForDiscovery();
  const base = defaultAccessItem(kind);
  return preset ? applyPolicyPreset(base, preset) : base;
}

function mergeListValue(values, nextValue) {
  const list = listValue(values);
  const value = String(nextValue || "").trim();
  if (value && !list.includes(value)) list.push(value);
  return list;
}

function mergeDiscoveredAccess(discovery) {
  ensureAccessDraft();
  syncAccessDetail();
  const identities = state.accessDraft.identity || {};
  const groups = state.accessDraft.group || {};
  state.accessDraft.identity = identities;
  state.accessDraft.group = groups;
  let newChats = 0;
  let newUsers = 0;
  let updated = 0;
  let selected = "";
  const chats = Array.isArray(discovery?.chats) ? discovery.chats : [];
  for (const chat of chats) {
    const chatId = String(chat.chat_id || "").trim();
    if (!chatId) continue;
    let groupKey = findGroupByChatId(chatId);
    if (!groupKey) {
      groupKey = uniqueAccessKey(groups, stableAccessKey("chat", chatId));
      groups[groupKey] = {
        ...defaultDiscoveredAccessItem("group"),
        label: chat.name || chatId,
        chat_ids: [chatId],
        members: [],
        aliases: [chat.name || ""].filter(Boolean),
      };
      newChats += 1;
      if (!selected) selected = `group:${groupKey}`;
    } else {
      const previousGroup = JSON.stringify(groups[groupKey] || {});
      groups[groupKey].label = groups[groupKey].label || chat.name || groupKey;
      groups[groupKey].chat_ids = mergeListValue(groups[groupKey].chat_ids, chatId);
      if (chat.name) groups[groupKey].aliases = mergeListValue(groups[groupKey].aliases, chat.name);
      if (JSON.stringify(groups[groupKey] || {}) !== previousGroup) updated += 1;
    }
    for (const member of chat.members || []) {
      const openId = String(member.open_id || "").trim();
      if (!openId || !openId.startsWith("ou_")) continue;
      const name = String(member.name || "").trim();
      let identityKey = findIdentityByOpenId(openId);
      if (!identityKey) {
        identityKey = uniqueAccessKey(identities, stableAccessKey("user", openId));
        identities[identityKey] = {
          ...defaultDiscoveredAccessItem("identity"),
          label: name || openId,
          open_ids: [openId],
          names: name ? [name] : [],
          emails: [],
          aliases: [],
        };
        newUsers += 1;
      } else if (name) {
        const previousIdentity = JSON.stringify(identities[identityKey] || {});
        identities[identityKey].label = identities[identityKey].label || name;
        identities[identityKey].names = mergeListValue(identities[identityKey].names, name);
        if (JSON.stringify(identities[identityKey] || {}) !== previousIdentity) updated += 1;
      }
    }
  }
  return { chats: chats.length, users: discovery?.member_count || 0, newChats, newUsers, updated, changed: !!(newChats || newUsers || updated), selected };
}

async function discoverAccessTargets() {
  const button = $("#discoverAccessBtn");
  if (button) button.disabled = true;
  setConfigMessage(t("discoveringAccess"));
  try {
    const discovery = await getJson("/api/discovery/bot-chats?include_members=1&page_limit=20");
    const summary = mergeDiscoveredAccess(discovery);
    if (summary.changed) {
      markAccessEditing();
      if (summary.selected) state.selectedAccessTarget = summary.selected;
    }
    renderAccessEditor({ skipSync: true });
    setConfigMessage(t("discoveredAccess", summary));
  } catch (error) {
    setConfigMessage(error.message);
  } finally {
    if (button) button.disabled = false;
  }
}

function getByPath(object, path) {
  return path.split(".").reduce((current, part) => current && current[part], object);
}

function setByPath(object, path, value) {
  const parts = path.split(".");
  let current = object;
  for (const part of parts.slice(0, -1)) {
    if (!current[part] || typeof current[part] !== "object") current[part] = {};
    current = current[part];
  }
  current[parts[parts.length - 1]] = value;
}

function pruneEmptyObject(object) {
  if (!object || typeof object !== "object" || Array.isArray(object)) return object;
  const result = {};
  for (const [key, value] of Object.entries(object)) {
    if (value && typeof value === "object" && !Array.isArray(value)) {
      const child = pruneEmptyObject(value);
      if (Object.keys(child).length) result[key] = child;
    } else if (value !== "" && value !== undefined && value !== null) {
      result[key] = value;
    }
  }
  return result;
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
  const canRestartDashboard = Boolean((status.dashboard_control || {}).can_restart);
  $("#restartDashboardBtn").disabled = !canRestartDashboard;
  $("#restartAllBtn").disabled = !canRestartDashboard;

  const config = status.dashboard || {};
  const nextRefreshMs = config.auto_refresh_sec ? Math.max(2, Number(config.auto_refresh_sec)) * 1000 : state.refreshMs;
  if (nextRefreshMs !== state.refreshMs) {
    state.refreshMs = nextRefreshMs;
    setAutoRefresh();
  }

  renderWindowsIntegration(status.windows_integration || {});

  const entries = [
    [t("codex"), caps.codex_cli],
    [t("codexHome"), caps.codex_home || status.codex_home],
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
  if (state.config && !isConfigInteracting()) {
    renderModelSelectOptions(state.config);
    renderServiceTierSelectOptions(state.config);
    renderRuntimeOptionsPreview();
  }
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
  const isAdminStartup = (item) => item.method === "scheduled_task_admin" || item.run_level === "Highest" || item.task?.run_level === "Highest";
  const startupHint = (item) => {
    if (isAdminStartup(item)) {
      return t("startupAdminTaskHint", { task: item.task_name || "-" });
    }
    if (item.method === "startup_folder") {
      return t("startupShortcutHint", { path: item.shortcut?.path || item.path || "-" });
    }
    return t("startupTaskHint", { task: item.task_name || "-" });
  };
  $("#dashboardStartupHint").textContent = startupHint(dashboardStartup);
  $("#connectionStartupHint").textContent = startupHint(connectionStartup);

  const folder = startMenu.folder || "";
  const integrationState = supported ? (controlEnabled ? t("available") : t("controlDisabled")) : t("unsupported");
  $("#windowsIntegrationDetail").textContent = t(folder ? "integrationDetail" : "integrationDetailNoFolder", { state: integrationState, folder });

  const canChange = supported && controlEnabled;
  setButton("#installStartMenuBtn", canChange && !startMenu.installed);
  setButton("#removeStartMenuBtn", canChange && (startMenu.installed || startMenu.partial || startMenu.manifest_exists));
  setButton("#enableDashboardStartupBtn", canChange && !dashboardStartup.installed);
  setButton("#enableDashboardStartupAdminBtn", canChange && !isAdminStartup(dashboardStartup));
  setButton("#disableDashboardStartupBtn", canChange && dashboardStartup.installed);
  setButton("#enableConnectionStartupBtn", canChange && !connectionStartup.installed);
  setButton("#enableConnectionStartupAdminBtn", canChange && !isAdminStartup(connectionStartup));
  setButton("#disableConnectionStartupBtn", canChange && connectionStartup.installed);
}

function formatBytes(value) {
  const size = Number(value || 0);
  if (!Number.isFinite(size) || size <= 0) return t("bytes", { count: 0 });
  if (size < 1024) return t("bytes", { count: size });
  const units = ["KB", "MB", "GB"];
  let amount = size / 1024;
  for (const unit of units) {
    if (amount < 1024 || unit === units[units.length - 1]) {
      return `${amount.toFixed(amount >= 10 ? 1 : 2)} ${unit}`;
    }
    amount /= 1024;
  }
  return t("bytes", { count: size });
}

function filePreviewHtml(file) {
  if (!file?.exists) {
    return `<p class="empty-copy">${escapeHtml(file?.error || t("missingFile"))}</p>`;
  }
  const href = escapeHtml(file.href || "");
  const type = String(file.content_type || "");
  const sourceType = String(file.type || "");
  if (type.startsWith("image/") || sourceType === "image") {
    return `<div class="file-preview"><img src="${href}" alt="${escapeHtml(file.name || file.label || "")}" loading="lazy" /></div>`;
  }
  if (type.startsWith("audio/")) {
    return `<div class="file-preview"><audio src="${href}" controls preload="metadata"></audio></div>`;
  }
  if (type.startsWith("video/")) {
    return `<div class="file-preview"><video src="${href}" controls preload="metadata"></video></div>`;
  }
  if (type === "application/pdf") {
    return `<div class="file-preview"><iframe src="${href}" title="${escapeHtml(file.name || file.label || "PDF")}"></iframe></div>`;
  }
  if (file.text_preview) {
    return `
      <pre class="file-text-preview">${escapeHtml(file.text_preview)}</pre>
      ${file.truncated ? `<p class="file-hint">${escapeHtml(t("previewTruncated"))}</p>` : ""}
    `;
  }
  return `<p class="empty-copy">${escapeHtml(t("noPreview"))}</p>`;
}

function fileCardHtml(file) {
  const label = file.label || file.type || file.kind || file.name || "file";
  const path = file.path ? `<code translate="no">${escapeHtml(file.path)}</code>` : "";
  const meta = [file.name, file.content_type, file.exists ? formatBytes(file.size) : ""].filter(Boolean).join(" · ");
  const open = file.exists && file.href ? `<a class="button-link" href="${escapeHtml(file.href)}" target="_blank" rel="noopener">${escapeHtml(t("openFile"))}</a>` : "";
  const error = file.error ? `<p class="warn-text">${escapeHtml(file.error)}</p>` : "";
  const fileKey = file.file_key ? `<p><span>file_key</span><code translate="no">${escapeHtml(file.file_key)}</code></p>` : "";
  return `
    <article class="job-file-card">
      <header>
        <div>
          <strong>${escapeHtml(label)}</strong>
          <span>${escapeHtml(meta || (file.exists ? t("available") : t("missingFile")))}</span>
        </div>
        ${open}
      </header>
      ${path}
      ${fileKey}
      ${error}
      ${filePreviewHtml(file)}
    </article>
  `;
}

function detailKvHtml(entries) {
  return entries
    .filter(([, value]) => value !== undefined && value !== null && value !== "")
    .map(([key, value]) => `<div><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
    .join("");
}

function renderJobDetail(detail) {
  const container = $("#jobDetail");
  if (!container) return;
  const summary = detail.summary || detail;
  const record = detail.record || detail;
  const files = detail.files || [];
  const attachments = detail.attachment_details || [];
  const events = detail.events || [];
  state.selectedJobId = String(summary.job_id || record.job_id || "");
  container.hidden = false;
  container.innerHTML = `
    <div class="job-detail-head">
      <div>
        <p class="eyebrow">${escapeHtml(t("jobDetails"))}</p>
        <h3 translate="no">${escapeHtml(state.selectedJobId)}</h3>
      </div>
      <button type="button" class="secondary" id="closeJobDetailBtn">${escapeHtml(t("closeDetails"))}</button>
    </div>
    <div class="job-detail-grid">
      <section>
        <h4>${escapeHtml(t("jobMetadata"))}</h4>
        <div class="detail-kv">
          ${detailKvHtml([
            ["status", statusLabel(jobStatus(summary))],
            ["kind", summary.job_kind],
            ["task", summary.task_id],
            ["workspace", summary.workspace],
            ["created", formatDateTime(summary.created_at)],
            ["updated", formatDateTime(summary.updated_at)],
            ["started", formatDateTime(summary.started_at)],
            ["finished", formatDateTime(summary.finished_at)],
            ["conversation", summary.conversation_key],
            ["resume session", summary.resume_session_id],
            ["message", summary.source?.message_id],
            ["chat", summary.source?.chat_id],
            ["sender", summary.source?.sender_id],
          ])}
        </div>
      </section>
      <section>
        <h4>${escapeHtml(t("jobFiles"))}</h4>
        <div class="job-file-grid">
          ${files.length ? files.map(fileCardHtml).join("") : `<p class="empty-copy">${escapeHtml(t("missingFile"))}</p>`}
        </div>
      </section>
      <section>
        <h4>${escapeHtml(t("inputAttachments"))}</h4>
        <div class="job-file-grid">
          ${attachments.length ? attachments.map(fileCardHtml).join("") : `<p class="empty-copy">${escapeHtml(t("noAttachments"))}</p>`}
        </div>
      </section>
      <section>
        <h4>${escapeHtml(t("jobTimeline"))}</h4>
        <div class="job-events">
          ${
            events.length
              ? events
                  .map(
                    (event) => `
                      <div>
                        <code>${escapeHtml(formatDateTime(event.ts))}</code>
                        <strong>${escapeHtml(event.event || "-")}</strong>
                        <pre>${escapeHtml(JSON.stringify(event.data || {}, null, 2))}</pre>
                      </div>
                    `,
                  )
                  .join("")
              : `<p class="empty-copy">${escapeHtml(t("noEvents"))}</p>`
          }
        </div>
      </section>
      <section>
        <h4>${escapeHtml(t("rawJobRecord"))}</h4>
        <pre class="raw-json">${escapeHtml(JSON.stringify(record, null, 2))}</pre>
      </section>
    </div>
  `;
  $("#closeJobDetailBtn")?.addEventListener("click", closeJobDetail);
}

function renderJobDetailLoading(jobId) {
  const container = $("#jobDetail");
  if (!container) return;
  container.hidden = false;
  container.innerHTML = `
    <div class="job-detail-head">
      <div>
        <p class="eyebrow">${escapeHtml(t("jobDetails"))}</p>
        <h3 translate="no">${escapeHtml(jobId)}</h3>
      </div>
      <button type="button" class="secondary" id="closeJobDetailBtn">${escapeHtml(t("closeDetails"))}</button>
    </div>
    <p class="message">${escapeHtml(t("loadingJobDetails"))}</p>
  `;
  $("#closeJobDetailBtn")?.addEventListener("click", closeJobDetail);
}

async function loadJobDetail(jobId) {
  state.selectedJobId = jobId;
  state.loadingJobDetail = true;
  if (state.lastJobs) renderJobs(state.lastJobs);
  renderJobDetailLoading(jobId);
  try {
    const detail = await getJson(`/api/jobs/${encodeURIComponent(jobId)}`);
    renderJobDetail(detail);
  } catch (error) {
    const container = $("#jobDetail");
    if (container) {
      container.hidden = false;
      container.innerHTML = `<p class="empty-copy">${escapeHtml(error.message)}</p>`;
    }
  } finally {
    state.loadingJobDetail = false;
  }
}

function closeJobDetail() {
  state.selectedJobId = "";
  const container = $("#jobDetail");
  if (container) {
    container.hidden = true;
    container.innerHTML = "";
  }
  if (state.lastJobs) renderJobs(state.lastJobs);
}

function bindJobDetailButtons() {
  document.querySelectorAll("[data-job-detail]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      loadJobDetail(button.dataset.jobDetail || "");
    });
  });
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
      const activeClass = state.selectedJobId === job.job_id ? " active" : "";
      return `
        <article class="job${activeClass}">
          <header>
            <code translate="no">${escapeHtml(job.job_id)}</code>
            ${pill(jobStatus(job))}
          </header>
          <p>${escapeHtml(text(job.workspace))} · ${escapeHtml(formatDateTime(job.updated_at))}</p>
          <p>${escapeHtml(job.prompt_prefix)}</p>
          <p>${escapeHtml(t("attachments", { count: job.attachment_count || 0 }))}</p>
          ${link}
          ${error}
          <button type="button" class="secondary job-detail-button" data-job-detail="${escapeHtml(job.job_id)}">${escapeHtml(t("viewDetails"))}</button>
        </article>
      `;
    })
    .join("");
  bindJobDetailButtons();
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
  state.configDraft = JSON.parse(JSON.stringify(state.config || {}));
  state.accessDraft = null;
  state.accessDirty = false;
  const writable = Boolean(configPayload.allow_config_write);
  const writeState = $("#configWriteState");
  writeState.textContent = writable ? t("writeEnabled") : t("readOnly");
  writeState.className = writable ? "pill ok" : "pill warn";
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
    state.lastConfigPayload = config;
    if (!isConfigInteracting()) renderConfig(config);
    $("#statusText").className = "";
  } catch (error) {
    $("#statusText").textContent = t("offline");
    setConfigMessage(error.message);
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

async function restartDashboard() {
  const message = $("#connectionMessage");
  const button = $("#restartDashboardBtn");
  button.disabled = true;
  message.textContent = t("restartingDashboard");
  try {
    await postJson("/api/dashboard/restart");
    message.textContent = t("dashboardRestarting");
    if (state.refreshTimer) {
      clearInterval(state.refreshTimer);
      state.refreshTimer = null;
    }
    setTimeout(waitForDashboardReconnect, 2500);
  } catch (error) {
    message.textContent = error.message;
    await refreshAll();
  }
}

async function restartAll() {
  const message = $("#connectionMessage");
  const buttons = ["#startConnectionBtn", "#stopConnectionBtn", "#restartDashboardBtn", "#restartAllBtn"]
    .map((selector) => $(selector))
    .filter(Boolean);
  buttons.forEach((button) => {
    button.disabled = true;
  });
  message.textContent = t("restartingAll");
  try {
    await postJson("/api/restart-all");
    message.textContent = t("allRestarting");
    if (state.refreshTimer) {
      clearInterval(state.refreshTimer);
      state.refreshTimer = null;
    }
    setTimeout(waitForDashboardReconnect, 2500);
  } catch (error) {
    message.textContent = error.message;
    await refreshAll();
  }
}

async function waitForDashboardReconnect(attempt = 0) {
  try {
    await getJson(`/api/status?restart_probe=${Date.now()}`);
    window.location.reload();
  } catch {
    if (attempt < 20) {
      setTimeout(() => waitForDashboardReconnect(attempt + 1), 800);
    } else {
      $("#connectionMessage").textContent = t("offline");
    }
  }
}

function windowsActionMessage(action) {
  const key = {
    "install-start-menu": "startMenuInstalled",
    "remove-start-menu": "startMenuRemoved",
    "enable-dashboard-startup": "dashboardStartupEnabled",
    "enable-dashboard-startup-admin": "dashboardStartupAdminEnabled",
    "disable-dashboard-startup": "dashboardStartupDisabled",
    "enable-connection-startup": "connectionStartupEnabled",
    "enable-connection-startup-admin": "connectionStartupAdminEnabled",
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
    "#enableDashboardStartupAdminBtn",
    "#disableDashboardStartupBtn",
    "#enableConnectionStartupBtn",
    "#enableConnectionStartupAdminBtn",
    "#disableConnectionStartupBtn",
  ];
  for (const id of buttons) setButton(id, false);
  message.textContent = action.endsWith("-admin") ? t("applyingAdmin") : t("applying");
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
  const skipped = [];
  syncGlobalConfigDraft();
  const draft = state.configDraft || state.config || {};
  for (const name of GLOBAL_CONFIG_FIELDS) {
    const oldValue = getByPath(state.config || {}, name);
    const value = getByPath(draft, name);
    if (name === "codex.home_dir" && !String(value || "").trim() && oldValue === undefined) {
      continue;
    }
    if (JSON.stringify(value) !== JSON.stringify(oldValue)) {
      addConfigUpdate(updates, skipped, name, value);
    }
  }
  syncAccessDetail();
  ensureAccessDraft();
  normalizeTemplateDrafts();
  const presetSyncChanged = syncPresetBackedPolicies();
  if (presetSyncChanged) state.accessDirty = true;
  const defaultPolicy = defaultPolicyFromTemplate();
  const defaultPolicyChanged = JSON.stringify(defaultPolicy) !== JSON.stringify(getByPath(state.config || {}, "access.default_policy") || {});
  if (defaultPolicyChanged) {
    addConfigUpdate(updates, skipped, "access.default_policy", defaultPolicy);
  }
  if (state.accessDirty || presetSyncChanged || defaultPolicyChanged) {
    const identities = state.accessDraft.identity || {};
    const userGroups = state.accessDraft.user_group || {};
    const groups = state.accessDraft.group || {};
    if (JSON.stringify(identities) !== JSON.stringify(getByPath(state.config || {}, "access.identities") || {})) {
      addConfigUpdate(updates, skipped, "access.identities", identities);
    }
    if (JSON.stringify(userGroups) !== JSON.stringify(getByPath(state.config || {}, "access.user_groups") || {})) {
      addConfigUpdate(updates, skipped, "access.user_groups", userGroups);
    }
    if (JSON.stringify(groups) !== JSON.stringify(getByPath(state.config || {}, "access.groups") || {})) {
      addConfigUpdate(updates, skipped, "access.groups", groups);
    }
  }
  return { updates, skipped };
}

async function applyConfig(event) {
  event.preventDefault();
  const { updates, skipped } = collectUpdates();
  if (!Object.keys(updates).length) {
    setConfigMessage(skipped.length ? t("skippedReadonly", { keys: skipped.join(", ") }) : t("noChanges"));
    state.configEditing = false;
    return;
  }
  try {
    setConfigMessage(t("applying"));
    const result = await postJson("/api/config", { updates });
    const restartKey = state.lastStatus?.feishu_connection?.running ? "connectionRestartRecommended" : "restartRecommended";
    const restart = result.restart_recommended ? ` · ${t(restartKey)}` : "";
    const skippedText = skipped.length ? ` · ${t("skippedReadonly", { keys: skipped.join(", ") })}` : "";
    setConfigMessage(`${t("changed", { keys: result.changed.join(", ") })}${restart}${skippedText}`);
    state.configEditing = false;
    await refreshAll();
  } catch (error) {
    setConfigMessage(error.message);
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
$("#restartDashboardBtn").addEventListener("click", restartDashboard);
$("#restartAllBtn").addEventListener("click", restartAll);
$("#installStartMenuBtn").addEventListener("click", () => controlWindowsIntegration("install-start-menu"));
$("#removeStartMenuBtn").addEventListener("click", () => controlWindowsIntegration("remove-start-menu"));
$("#enableDashboardStartupBtn").addEventListener("click", () => controlWindowsIntegration("enable-dashboard-startup"));
$("#enableDashboardStartupAdminBtn").addEventListener("click", () => controlWindowsIntegration("enable-dashboard-startup-admin"));
$("#disableDashboardStartupBtn").addEventListener("click", () => controlWindowsIntegration("disable-dashboard-startup"));
$("#enableConnectionStartupBtn").addEventListener("click", () => controlWindowsIntegration("enable-connection-startup"));
$("#enableConnectionStartupAdminBtn").addEventListener("click", () => controlWindowsIntegration("enable-connection-startup-admin"));
$("#disableConnectionStartupBtn").addEventListener("click", () => controlWindowsIntegration("disable-connection-startup"));
$("#addIdentityBtn").addEventListener("click", () => addAccessCard("identity"));
$("#addUserGroupBtn").addEventListener("click", () => addAccessCard("user_group"));
$("#addGroupBtn").addEventListener("click", () => addAccessCard("group"));
$("#discoverAccessBtn").addEventListener("click", discoverAccessTargets);
$("#autoRefresh").addEventListener("change", setAutoRefresh);
$("#configForm").addEventListener("submit", applyConfig);
$("#configForm").addEventListener("input", (event) => {
  if (event.target?.id === "configTargetSearch") return;
  markConfigEditing();
});
$("#configForm").addEventListener("change", (event) => {
  if (event.target?.id === "configTargetSearch") return;
  markConfigEditing();
});
$("#configWorkbench").addEventListener("input", markAccessEditorDirty);
$("#configWorkbench").addEventListener("change", markAccessEditorDirty);

applyLanguage();
refreshAll().then(setAutoRefresh);
