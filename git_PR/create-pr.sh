#!/usr/bin/env bash
set -e

# ---------------------------------------------------------------------------
# create-pr.sh  –  Push current branch and open a GitHub Pull Request
# Usage:  ./create-pr.sh [base-branch] [pr-title] [pr-body]
# Defaults: base=main, title prompted if omitted, body optional
# ---------------------------------------------------------------------------

BASE_BRANCH="${1:-main}"
PR_TITLE="${2:-}"
PR_BODY="${3:-}"

# Require gh CLI
if ! command -v gh &>/dev/null; then
    echo "Error: GitHub CLI (gh) is not installed. Install from https://cli.github.com/"
    exit 1
fi

# Current branch
HEAD_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$HEAD_BRANCH" = "$BASE_BRANCH" ]; then
    echo "You are on '$BASE_BRANCH'. Switch to a feature/develop branch first."
    exit 1
fi

# Push the current branch (set upstream if needed)
echo "Pushing '$HEAD_BRANCH' to origin..."
git push --set-upstream origin "$HEAD_BRANCH"

# Prompt for PR title if not supplied
if [ -z "$PR_TITLE" ]; then
    read -rp "PR title: " PR_TITLE
fi

if [ -z "$PR_TITLE" ]; then
    echo "PR title cannot be empty. Exiting."
    exit 1
fi

# Prompt for PR body if not supplied
if [ -z "$PR_BODY" ]; then
    read -rp "PR body (optional, press Enter to skip): " PR_BODY
fi

# Build gh command
GH_ARGS=(pr create --base "$BASE_BRANCH" --head "$HEAD_BRANCH" --title "$PR_TITLE")

if [ -n "$PR_BODY" ]; then
    GH_ARGS+=(--body "$PR_BODY")
else
    GH_ARGS+=(--body "")
fi

echo ""
echo "Creating PR: '$HEAD_BRANCH' → '$BASE_BRANCH'"
gh "${GH_ARGS[@]}"

echo ""
echo "Pull request created successfully."
