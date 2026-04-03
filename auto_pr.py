import subprocess
import sys
import urllib.request
import urllib.error
import json
import os

from config import GH_TOKEN, GH_REPO

BASE = "main"

def run(cmd, capture=False):
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if result.returncode != 0:
        print(result.stderr.strip() if result.stderr else "Command failed.")
        sys.exit(1)
    return result.stdout.strip() if capture else None

def get_repo_owner():
    remote = run("git remote get-url origin", capture=True)
    remote = remote.replace(".git", "")
    if "github.com/" in remote:
        parts = remote.split("github.com/")[-1]
    elif "github.com:" in remote:
        parts = remote.split("github.com:")[-1]
    else:
        print("Could not detect GitHub repo from remote URL.")
        sys.exit(1)
    owner = parts.strip("/").split("/")[0]
    return owner

def create_pr(owner, head, title, body=""):
    url = f"https://api.github.com/repos/{owner}/{GH_REPO}/pulls"
    data = json.dumps({"title": title, "body": body, "head": head, "base": BASE}).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"token {GH_TOKEN}",
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
        msg = error.get("message", str(e))
        # PR already exists — not a fatal error
        if "already exists" in msg:
            print(f"PR already exists for '{head}' -> '{BASE}'.")
            return None
        print(f"GitHub API error: {msg}")
        sys.exit(1)

# ── Current branch ──────────────────────────────────────────────
current_branch = run("git rev-parse --abbrev-ref HEAD", capture=True)

if current_branch == BASE:
    print(f"You are on '{BASE}'. Switch to a feature or develop branch first.")
    sys.exit(1)

# ── Check for changes ───────────────────────────────────────────
status = run("git status --porcelain", capture=True)
if not status:
    print("No changes to commit.")
else:
    print("\nChanged files:")
    run("git status --short")

    commit_msg = input("\nEnter commit message: ").strip()
    if not commit_msg:
        print("Commit message cannot be empty. Exiting.")
        sys.exit(1)

    run("git add .")
    run(f'git commit -m "{commit_msg}"')
    print("Changes committed.")

# ── Push branch ─────────────────────────────────────────────────
print(f"\nPushing '{current_branch}' to origin...")
run(f"git push --set-upstream origin {current_branch}")

# ── Auto create PR ──────────────────────────────────────────────
owner = get_repo_owner()
last_commit_msg = run("git log -1 --pretty=%s", capture=True)

print(f"\nCreating PR: '{current_branch}' -> '{BASE}'")
pr_url = create_pr(owner, current_branch, last_commit_msg)

if pr_url:
    print(f"\nPull request created successfully.")
    print(f"URL: {pr_url}")
