param(
  [string]$AppId = $env:LARK_APP_ID,
  [string]$Brand = "feishu",
  [string]$SecretPath = "$env:USERPROFILE\.codex\.sandbox-secrets\feishu-lark-cli.json",
  [ValidateSet("auto", "bot", "user")]
  [string]$DefaultAs = "auto",
  [switch]$RefreshStoredSecret,
  [switch]$NoStoreSecret,
  [switch]$LoginUser,
  [switch]$SkipLogin
)

$ErrorActionPreference = "Stop"
if (-not $env:LARK_CLI_NO_PROXY) {
  $env:LARK_CLI_NO_PROXY = "1"
}

function Resolve-CommandPath {
  param([string]$Name)
  $cmd = Get-Command $Name -ErrorAction Stop
  if ($cmd.Source -like "*.ps1") {
    $candidate = [System.IO.Path]::ChangeExtension($cmd.Source, ".cmd")
    if (Test-Path -LiteralPath $candidate) {
      return $candidate
    }
  }
  return $cmd.Source
}

function Protect-SecretPath {
  param([string]$Path)
  try {
    $account = "$($env:USERDOMAIN)\$($env:USERNAME)"
    $dir = Split-Path -Parent $Path
    if ($dir) {
      & icacls $dir /inheritance:r /grant:r "${account}:(OI)(CI)F" "SYSTEM:(OI)(CI)F" "Administrators:(OI)(CI)F" | Out-Null
    }
    if (Test-Path -LiteralPath $Path) {
      & icacls $Path /inheritance:r /grant:r "${account}:F" "SYSTEM:F" "Administrators:F" | Out-Null
    }
  } catch {
    Write-Warning "Could not tighten ACL for secret file: $($_.Exception.Message)"
  }
}

function Read-StoredSecret {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) { return $null }
  $profile = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
  if (-not $profile.app_secret) { return $null }
  return $profile
}

function Save-StoredSecret {
  param(
    [string]$Path,
    [string]$StoredAppId,
    [string]$StoredBrand,
    [string]$StoredSecret
  )
  $dir = Split-Path -Parent $Path
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  [ordered]@{
    app_id = $StoredAppId
    brand = $StoredBrand
    app_secret = $StoredSecret
    updated_at = (Get-Date).ToString("o")
    note = "Plaintext secret for portable Codex user-dir migration. Keep this directory private."
  } | ConvertTo-Json | Set-Content -LiteralPath $Path -Encoding UTF8
  Protect-SecretPath -Path $Path
}

$larkCli = Resolve-CommandPath "lark-cli"

if (-not $AppId) {
  throw "Missing AppId. Pass -AppId or set LARK_APP_ID."
}

Write-Host "Initializing lark-cli for App ID: $AppId"
Write-Host "Secret profile: $SecretPath"
Write-Host "The App Secret is passed to lark-cli through stdin, never as a process argument."

$stored = $null
if (-not $RefreshStoredSecret) {
  $stored = Read-StoredSecret -Path $SecretPath
}

if ($stored) {
  $AppId = [string]$stored.app_id
  $Brand = [string]$stored.brand
  $plain = [string]$stored.app_secret
  Write-Host "Using stored lark-cli app secret from Codex user directory."
} else {
  $secret = Read-Host -AsSecureString "Lark App Secret"
  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
  try {
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringUni($bstr)
  } finally {
    if ($bstr -ne [IntPtr]::Zero) {
      [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
    Remove-Variable secret -ErrorAction SilentlyContinue
  }

  if (-not $NoStoreSecret) {
    Save-StoredSecret -Path $SecretPath -StoredAppId $AppId -StoredBrand $Brand -StoredSecret $plain
    Write-Host "Stored app secret under Codex user directory."
  }
}

try {
  $plain | & $larkCli config init --app-id $AppId --app-secret-stdin --brand $Brand
} finally {
  Remove-Variable plain -ErrorAction SilentlyContinue
}

& $larkCli config default-as $DefaultAs | Out-Null

if ($LoginUser -and -not $SkipLogin) {
  throw "User auth is not performed by this initializer. Use patched lark-cli auth login --app-scopes separately only when the user explicitly asks for user authorization."
}

& $larkCli auth status
& $larkCli doctor
