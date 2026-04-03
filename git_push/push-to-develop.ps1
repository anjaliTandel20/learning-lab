param(
    [string]$CommitMessage = ""
)

$ErrorActionPreference = "Stop"

# Ensure we're on the develop branch
$currentBranch = git rev-parse --abbrev-ref HEAD
if ($currentBranch -ne "develop") {
    Write-Host "Switching from '$currentBranch' to 'develop'..."
    git checkout develop
}

# Check for changes
$status = git status --porcelain
if (-not $status) {
    Write-Host "No changes to commit. Exiting."
    exit 0
}

# Show summary of changed files
Write-Host "`nChanged files:"
git status --short

# Prompt for commit message if not provided
if (-not $CommitMessage) {
    $CommitMessage = Read-Host "`nEnter commit message"
}

if (-not $CommitMessage) {
    Write-Host "Commit message cannot be empty. Exiting."
    exit 1
}

# Stage, commit, and push
git add .
git commit -m $CommitMessage
git push origin develop

Write-Host "`nPushed to origin/develop successfully."
