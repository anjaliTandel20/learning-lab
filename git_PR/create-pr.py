import subprocess
import sys
import urllib.request
import urllib.error
import json
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import GH_TOKEN

def run(cmd, capture=False):
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if result.returncode != 0:
        print(result.stderr.strip() if result.stderr else "Command failed.")
        sys.exit(1)
    return result.stdout.strip() if capture else None

def get_repo_info():
    remote = run("git remote get-url origin", capture=True)
    # Handles both https://github.com/owner/repo.git and git@github.com:owner/repo.git
    remote = remote.replace(".git", "")
    if "github.com/" in remote:
        parts = remote.split("github.com/")[-1]
    elif "github.com:" in remote:
        parts = remote.split("github.com:")[-1]
    else:
        print("Could not detect GitHub repo from remote URL.")
        sys.exit(1)
    owner, repo = parts.strip("/").split("/")
    return owner, repo

def create_pr(token, owner, repo, head, base, title, body):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    data = json.dumps({"title": title, "body": body, "head": head, "base": base}).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as res:
            pr = json.loads(res.read())
            return pr["html_url"]
    except urllib.error.HTTPError as e:
        error = json.loads(e.read())
        print(f"GitHub API error: {error.get('message', str(e))}")
        sys.exit(1)

BASE = "main"

# Get current branch
current_branch = run("git rev-parse --abbrev-ref HEAD", capture=True)

if current_branch == BASE:
    print(f"You are on '{BASE}'. Switch to your feature or develop branch first.")
    sys.exit(1)

# Check for uncommitted changes
status = run("git status --porcelain", capture=True)
if status:
    print("\nUncommitted changes detected:")
    run("git status --short")
    commit_msg = input("\nEnter commit message to commit changes (or press Enter to skip): ").strip()
    if commit_msg:
        run("git add .")
        run(f'git commit -m "{commit_msg}"')
        print("Changes committed.")

# Push branch
print(f"\nPushing '{current_branch}' to origin...")
run(f"git push --set-upstream origin {current_branch}")

# GitHub token from config
token = GH_TOKEN

# Detect owner/repo from remote
owner, repo = get_repo_info()
print(f"Repo detected: {owner}/{repo}")

# PR title
pr_title = input("\nEnter PR title: ").strip()
if not pr_title:
    print("PR title cannot be empty. Exiting.")
    sys.exit(1)

# PR body
pr_body = input("Enter PR body (optional, press Enter to skip): ").strip()

# Create PR
print(f"\nCreating PR: '{current_branch}' -> '{BASE}'")
pr_url = create_pr(token, owner, repo, current_branch, BASE, pr_title, pr_body)

print(f"\nPull request created successfully.")
print(f"URL: {pr_url}")
