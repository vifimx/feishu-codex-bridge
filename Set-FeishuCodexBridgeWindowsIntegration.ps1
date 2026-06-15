param(
  [ValidateSet(
    "status",
    "install-start-menu",
    "remove-start-menu",
    "enable-dashboard-startup",
    "enable-dashboard-startup-admin",
    "disable-dashboard-startup",
    "enable-connection-startup",
    "enable-connection-startup-admin",
    "disable-connection-startup"
  )]
  [string]$Action = "status",
  [string]$ConfigPath = "$PSScriptRoot\bridge.config.json"
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

function Resolve-Python {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) { return $python.Source }
  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) { return $py.Source }
  throw "Python was not found. Install Python or add it to PATH."
}

$bridge = Join-Path $PSScriptRoot "feishu_codex_bridge.py"
if (-not (Test-Path -LiteralPath $bridge)) {
  throw "Bridge runtime not found: $bridge"
}

$pythonExe = Resolve-Python
& $pythonExe -u $bridge --config $ConfigPath --windows-integration $Action
