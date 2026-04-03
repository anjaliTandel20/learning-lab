import subprocess
import sys
import urllib.request
import urllib.error
import json
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import GH_TOKEN, GH_REPO

BASE = "main"

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr.strip())
        sys.exit(1)
    return result.stdout.strip()

def get_owner():
    remote = run("git remote get-url origin").replace(".git", "")
    if "github.com/" in remote:
        parts = remote.split("github.com/")[-1]
    elif "github.com:" in remote:
        parts = remote.split("github.com:")[-1]
    else:
        print("Could not detect GitHub repo from remote URL.")
        sys.exit(1)
    return parts.strip("/").split("/")[0]

def create_pr(owner, head, title, body=""):
    url = f"https://api.github.com/repos/{owner}/{GH_REPO}/pulls"
    data = json.dumps({"title": title, "body": body, "head": head, "base": BASE}).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Authorization": f"token {GH_TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read())["html_url"]
    except urllib.error.HTTPError as e:
        error = json.loads(e.read())
        msg = error.get("message", str(e))
        if "already exists" in msg:
            print(f"A PR already exists for this branch.")
            sys.exit(0)
        print(f"GitHub API error: {msg}")
        sys.exit(1)

# Current branch
current_branch = run("git rev-parse --abbrev-ref HEAD")

if current_branch == BASE:
    print(f"You are on '{BASE}'. Switch to your feature or develop branch first.")
    sys.exit(1)

# Use last commit message as PR title automatically
pr_title = run("git log -1 --pretty=%s")

print(f"\nBranch : {current_branch}")
print(f"Base   : {BASE}")
print(f"Title  : {pr_title}")

confirm = input("\nCreate PR with above details? (Enter to confirm / type new title to change): ").strip()
if confirm:
    pr_title = confirm

# Create PR
owner = get_owner()
print(f"\nCreating PR: '{current_branch}' -> '{BASE}'")
pr_url = create_pr(owner, current_branch, pr_title)

print(f"\nPull request created successfully.")
print(f"URL: {pr_url}")
