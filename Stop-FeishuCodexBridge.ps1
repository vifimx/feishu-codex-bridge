param(
  [string]$ConfigPath = "$PSScriptRoot\bridge.config.json"
)

$ErrorActionPreference = "SilentlyContinue"

$state = Join-Path $env:USERPROFILE ".codex\tmp\feishu-codex-bridge"
if (Test-Path -LiteralPath $ConfigPath) {
  $config = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
  if ($config.state_dir) {
    $state = [string]$config.state_dir
  }
}
$pidFiles = @(
  (Join-Path $state "bridge.pid"),
  (Join-Path $state "dashboard.pid"),
  (Join-Path $state "private-poller.pid")
)

foreach ($pidFile in $pidFiles) {
  if (Test-Path -LiteralPath $pidFile) {
    $pidValue = Get-Content -LiteralPath $pidFile | Select-Object -First 1
    if ($pidValue) {
      Stop-Process -Id ([int]$pidValue) -Force
    }
    Remove-Item -LiteralPath $pidFile -Force
  }
}

$jobsDir = Join-Path $state "jobs"
if (Test-Path -LiteralPath $jobsDir) {
  Get-ChildItem -LiteralPath $jobsDir -Filter "job-*.json" | ForEach-Object {
    $job = Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json
    if ($job.status -in @("queued", "running")) {
      foreach ($pidName in @("worker_pid", "runner_pid", "codex_pid")) {
        $pidValue = $job.$pidName
        if ($pidValue) {
          Stop-Process -Id ([int]$pidValue) -Force
        }
      }
      $job.status = "stopped"
      $job.updated_at = (Get-Date).ToUniversalTime().ToString("o")
      $job.error = "Stopped by Stop-FeishuCodexBridge.ps1"
      $job | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $_.FullName -Encoding UTF8
    }
  }
}

Get-Process lark-cli | Stop-Process -Force

Write-Output "Feishu Codex bridge stopped."
