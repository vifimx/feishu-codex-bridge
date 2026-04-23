param(
  [string]$Hostname = "github.com",
  [ValidateSet("https", "ssh")]
  [string]$GitProtocol = "https",
  [string[]]$Scopes = @("repo", "workflow", "read:org", "gist"),
  [switch]$Login,
  [switch]$TokenPrompt,
  [switch]$SetupGit,
  [switch]$CreateLocalEnv,
  [string]$LocalEnvPath = "$PSScriptRoot\.local\github.env.ps1"
)

$ErrorActionPreference = "Stop"

function Resolve-Gh {
  $cmd = Get-Command gh -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }

  $candidates = @(
    "C:\Program Files\GitHub CLI\gh.exe",
    "C:\Program Files (x86)\GitHub CLI\gh.exe",
    "$env:LOCALAPPDATA\GitHub CLI\gh.exe"
  )
  foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) { return $candidate }
  }

  throw "GitHub CLI gh was not found. Install with: winget install --id GitHub.cli -e"
}

function ConvertFrom-SecureStringToPlainText {
  param([Security.SecureString]$Secure)
  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secure)
  try {
    return [Runtime.InteropServices.Marshal]::PtrToStringUni($bstr)
  } finally {
    if ($bstr -ne [IntPtr]::Zero) {
      [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
  }
}

function New-LocalEnvTemplate {
  param([string]$Path)
  $dir = Split-Path -Parent $Path
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  if (Test-Path -LiteralPath $Path) {
    Write-Host "Local env file already exists: $Path"
    return
  }
  @'
# Local GitHub auth environment for Feishu Codex Bridge.
# This file is intentionally ignored by git. Do not commit token values.
#
# Preferred auth is `gh auth login --web`, which stores credentials in the
# Windows credential store when available.
#
# For headless/fine-grained-token flows, uncomment this line and paste a token
# locally. Keep file ACLs private.
# $env:GH_TOKEN = "github_pat_xxx"
#
# Optional:
# $env:GH_HOST = "github.com"
'@ | Set-Content -LiteralPath $Path -Encoding UTF8
  Write-Host "Created local env template: $Path"
}

$gh = Resolve-Gh
Write-Host "gh: $gh"
& $gh --version

if ($CreateLocalEnv) {
  New-LocalEnvTemplate -Path $LocalEnvPath
}

if ($TokenPrompt) {
  Write-Host "Paste a GitHub token. Input is hidden and will be piped to gh; it will not be printed."
  $secure = Read-Host -AsSecureString "GitHub token"
  $plain = ConvertFrom-SecureStringToPlainText -Secure $secure
  try {
    $plain | & $gh auth login --hostname $Hostname --with-token
  } finally {
    Remove-Variable plain -ErrorAction SilentlyContinue
  }
}

if ($Login) {
  $scopeArg = ($Scopes -join ",")
  & $gh auth login --hostname $Hostname --web --clipboard --git-protocol $GitProtocol --scopes $scopeArg
}

if ($SetupGit) {
  & $gh auth setup-git --hostname $Hostname
}

& $gh auth status --hostname $Hostname
