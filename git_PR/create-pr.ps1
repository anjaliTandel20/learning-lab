param(
    [string]$PRTitle = "",
    [string]$PRBody  = "",
    [string]$Base    = "main"
)

$ErrorActionPreference = "Stop"

# Require gh CLI
$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) {
    Write-Host "GitHub CLI (gh) is not installed. Install from https://cli.github.com/"
    exit 1
}

# Current branch
$currentBranch = git rev-parse --abbrev-ref HEAD

if ($currentBranch -eq $Base) {
    Write-Host "You are on '$Base'. Please switch to your feature or develop branch first."
    exit 1
}

# Check for uncommitted changes and offer to commit them
$status = git status --porcelain
if ($status) {
    Write-Host "`nUncommitted changes detected:"
    git status --short

    $commitMsg = Read-Host "`nEnter commit message to commit changes (or press Enter to skip)"
    if ($commitMsg) {
        git add .
        git commit -m $commitMsg
        Write-Host "Changes committed."
    }
}

# Push current branch
Write-Host "`nPushing '$currentBranch' to origin..."
git push --set-upstream origin $currentBranch

# Prompt for PR title
if (-not $PRTitle) {
    $PRTitle = Read-Host "`nEnter PR title"
}
if (-not $PRTitle) {
    Write-Host "PR title cannot be empty. Exiting."
    exit 1
}

# Prompt for PR body
if (-not $PRBody) {
    $PRBody = Read-Host "Enter PR body (optional, press Enter to skip)"
}

# Create the PR
Write-Host "`nCreating PR: '$currentBranch' -> '$Base'"
gh pr create --base $Base --head $currentBranch --title $PRTitle --body $PRBody

Write-Host "`nPull request created successfully."
