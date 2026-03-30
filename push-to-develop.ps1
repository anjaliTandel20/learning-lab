# Automates staging, committing, and pushing to the develop branch

param(
    [string]$Message = ""
)

$BRANCH = "develop"

# Ensure we're on the develop branch
$currentBranch = git rev-parse --abbrev-ref HEAD
if ($currentBranch -ne $BRANCH) {
    Write-Host "Switching to $BRANCH branch..."
    git checkout $BRANCH
}

# Check for changes
$status = git status --porcelain
if (-not $status) {
    Write-Host "Nothing to commit. Working tree is clean."
    exit 0
}

# Show what will be committed
Write-Host "=== Changes to be committed ==="
git status --short

# Prompt for commit message if not provided as argument
if (-not $Message) {
    $Message = Read-Host "Enter commit message"
    if (-not $Message) {
        Write-Host "Commit message cannot be empty."
        exit 1
    }
}

# Stage all changes, commit, and push
git add .
git commit -m $Message
git push origin $BRANCH

Write-Host ""
Write-Host "Successfully pushed to $BRANCH."
