# GitHub Authentication

This project uses the GitHub CLI (`gh`) for repository creation, remotes, pushes, pull requests, and GitHub Actions inspection.

## Install

On Windows:

```powershell
winget install --id GitHub.cli -e --source winget
```

If the current shell cannot find `gh` immediately after installation, open a new PowerShell window or use:

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" --version
```

## Preferred Login

Use browser login. `gh` stores credentials in the Windows credential store when available.

```powershell
powershell -ExecutionPolicy Bypass -File .\Initialize-GitHubCli.ps1 -Login -SetupGit
```

Requested default scopes:

```text
repo, workflow, read:org, gist
```

Use fewer scopes when possible.

## Token Login

For a personal access token flow:

```powershell
powershell -ExecutionPolicy Bypass -File .\Initialize-GitHubCli.ps1 -TokenPrompt -SetupGit
```

The script reads the token as a hidden secure prompt and pipes it to `gh auth login --with-token`. It does not print the token.

## Local Shell Token File

For headless or fine-grained-token flows, create a local ignored file:

```powershell
powershell -ExecutionPolicy Bypass -File .\Initialize-GitHubCli.ps1 -CreateLocalEnv
```

This creates:

```text
.local\github.env.ps1
```

The file is ignored by git. If used, it may contain:

```powershell
$env:GH_TOKEN = "github_pat_xxx"
```

Do not commit token values. Prefer the Windows credential store when possible.

## Status

```powershell
powershell -ExecutionPolicy Bypass -File .\Initialize-GitHubCli.ps1
```

or:

```powershell
gh auth status
```

## Create GitHub Remote

After login, create a private GitHub repository and push:

```powershell
gh repo create feishu-codex-bridge --private --source . --remote origin --push
```

For an existing empty repo:

```powershell
git remote add origin https://github.com/<owner>/feishu-codex-bridge.git
git push -u origin main
```

Keep this repository private until `bridge.config.example.json`, README, and history are checked for deployment-specific identifiers.
