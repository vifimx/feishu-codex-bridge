param(
  [string]$ConfigPath = "$PSScriptRoot\bridge.config.json",
  [switch]$DryRun,
  [switch]$PrivatePollerOnly,
  [switch]$NoPrivatePoller
)

$ErrorActionPreference = "Stop"
$env:LARK_CLI_NO_PROXY = "1"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

[Console]::InputEncoding = [System.Text.Encoding]::UTF8
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
$argsToRun = @("-u", $bridge, "--config", $ConfigPath)
if ($DryRun) { $argsToRun += "--dry-run" }
if ($PrivatePollerOnly) { $argsToRun += "--private-poller-only" }
if ($NoPrivatePoller) { $argsToRun += "--no-private-poller" }

& $pythonExe @argsToRun
