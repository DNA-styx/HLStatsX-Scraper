import requests
import os

# Function to get forks of a repository
def get_forks(owner, repo, token):
    forks = []
    url = f"https://api.github.com/repos/{owner}/{repo}/forks"
    headers = {"Authorization": f"token {token}"}
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        forks.extend(response.json())
        url = response.links.get("next", {}).get("url")
    return forks

# Function to get unique commit SHAs of a repository
def get_unique_commits(owner, repo, token):
    commits = set()
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {"Authorization": f"token {token}"}
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        for commit in response.json():
            commits.add(commit["sha"])
        url = response.links.get("next", {}).get("url")
    return commits

# Gather activity data recursively for forks and forks of forks
def gather_activity(owner, repo, token, depth=0, max_depth=1):
    if depth > max_depth:
        return []

    forks = get_forks(owner, repo, token)
    fork_activity = []

    for fork in forks:
        fork_owner = fork["owner"]["login"]
        fork_repo = fork["name"]
        commits = get_unique_commits(fork_owner, fork_repo, token)

        # Exclude forks with no code changes
        if commits:
            fork_activity.append({"fork": fork, "commits": len(commits)})
            # Recursively gather activity data for forks of forks
            fork_activity.extend(gather_activity(fork_owner, fork_repo, token, depth + 1, max_depth))

    return fork_activity

# Generate HTML page
def generate_html(fork_activity):
    html = "<html><head><title>Fork Activity</title></head><body>"
    html += "<h1>Fork Activity</h1><ul>"
    for activity in fork_activity:
        repo_url = activity['fork']['html_url']
        repo_name = activity['fork']['full_name']
        commits = activity['commits']
        html += f'<li><a href="{repo_url}" target="_blank">{repo_name}</a>: {commits} commits</li>'
    html += "</ul></body></html>"

    os.makedirs("public", exist_ok=True)
    with open("public/index.html", "w") as f:
        f.write(html)

# Main function
def main():
    owner = "octocat"
    repo = "hlstatsx-community-edition"
    token = os.getenv("GITHUB_TOKEN")

    fork_activity = gather_activity(owner, repo, token, max_depth=2) # Adjust max_depth as needed
    # Remove duplicates by full_name
    unique_activity = {activity['fork']['full_name']: activity for activity in fork_activity}.values()
    generate_html(unique_activity)

if __name__ == "__main__":
    main()
