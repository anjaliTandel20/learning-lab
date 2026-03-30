#!/usr/bin/env bash
set -e

COMMIT_MESSAGE="${1:-}"

# Ensure we're on the develop branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "develop" ]; then
    echo "Switching from '$current_branch' to 'develop'..."
    git checkout develop
fi

# Check for changes
if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to commit. Exiting."
    exit 0
fi

# Show summary of changed files
echo ""
echo "Changed files:"
git status --short

# Prompt for commit message if not provided
if [ -z "$COMMIT_MESSAGE" ]; then
    read -rp $'\nEnter commit message: ' COMMIT_MESSAGE
fi

if [ -z "$COMMIT_MESSAGE" ]; then
    echo "Commit message cannot be empty. Exiting."
    exit 1
fi

# Stage, commit, and push
git add .
git commit -m "$COMMIT_MESSAGE"
git push origin develop

echo ""
echo "Pushed to origin/develop successfully."
