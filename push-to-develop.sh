#!/bin/bash
# Automates staging, committing, and pushing to the develop branch

set -e  # Exit on any error

BRANCH="develop"

# Ensure we're on the develop branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "$BRANCH" ]; then
  echo "Switching to $BRANCH branch..."
  git checkout "$BRANCH"
fi

# Check for changes
if [ -z "$(git status --porcelain)" ]; then
  echo "Nothing to commit. Working tree is clean."
  exit 0
fi

# Show what will be committed
echo "=== Changes to be committed ==="
git status --short

# Prompt for commit message if not provided as argument
if [ -n "$1" ]; then
  COMMIT_MSG="$1"
else
  read -rp "Enter commit message: " COMMIT_MSG
  if [ -z "$COMMIT_MSG" ]; then
    echo "Commit message cannot be empty."
    exit 1
  fi
fi

# Stage all changes, commit, and push
git add .
git commit -m "$COMMIT_MSG"
git push origin "$BRANCH"

echo ""
echo "Successfully pushed to $BRANCH."
