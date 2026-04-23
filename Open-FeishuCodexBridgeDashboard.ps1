param(
  [string]$ConfigPath = "$PSScriptRoot\bridge.config.json",
  [string]$HostName = "127.0.0.1",
  [int]$Port = 8765,
  [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$env:LARK_CLI_NO_PROXY = "1"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

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
$config = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
$stateDir = [string]$config.state_dir
if (-not $stateDir) {
  $stateDir = Join-Path $env:USERPROFILE ".codex\tmp\feishu-codex-bridge"
}
New-Item -ItemType Directory -Force -Path $stateDir | Out-Null

$pidFile = Join-Path $stateDir "dashboard.pid"
if (Test-Path -LiteralPath $pidFile) {
  $pidValue = Get-Content -LiteralPath $pidFile | Select-Object -First 1
  if ($pidValue -and (Get-Process -Id ([int]$pidValue) -ErrorAction SilentlyContinue)) {
    $url = "http://${HostName}:$Port/"
    if (-not $NoBrowser) { Start-Process $url }
    Write-Output "Dashboard already running: $url"
    exit 0
  }
  Remove-Item -LiteralPath $pidFile -Force
}

$out = Join-Path $stateDir "dashboard.stdout.log"
$err = Join-Path $stateDir "dashboard.stderr.log"
$argsToRun = @(
  "-u",
  $bridge,
  "--config",
  $ConfigPath,
  "--dashboard-only",
  "--dashboard-host",
  $HostName,
  "--dashboard-port",
  [string]$Port
)

$proc = Start-Process -FilePath $pythonExe -ArgumentList $argsToRun -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err -PassThru
$proc.Id | Set-Content -LiteralPath $pidFile -Encoding ASCII

$url = "http://${HostName}:$Port/"
$deadline = (Get-Date).AddSeconds(10)
do {
  try {
    Invoke-WebRequest -UseBasicParsing -Uri "$url/api/status" -TimeoutSec 2 | Out-Null
    if (-not $NoBrowser) { Start-Process $url }
    Write-Output "Dashboard started: $url"
    exit 0
  } catch {
    Start-Sleep -Milliseconds 300
  }
} while ((Get-Date) -lt $deadline)

Write-Output "Dashboard process started but health check did not answer yet: $url"
Write-Output "stdout: $out"
Write-Output "stderr: $err"
