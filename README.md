# HackSonTest

This repository demonstrates how to:

- Create a GitHub Action that can be triggered externally (via the `repository_dispatch` event)
- Trigger that workflow directly from any environment using a simple `curl` call to the GitHub API (no local server required)

## Project Structure

- `.github/workflows/external-trigger.yml`: GitHub Actions workflow that can be triggered externally

## 1. Prepare a GitHub Access Token

1. Create a Personal Access Token on GitHub:
	- Recommended: use a fine-grained PAT and grant at least `Actions` / `Contents` permissions for this repository (or use a classic PAT with `repo` scope).
2. Set environment variables on your machine (replace placeholders with your own values):

```bash
export GITHUB_TOKEN="<your_pat_here>"
export GITHUB_OWNER="rock-57blocks"     # Repository owner
export GITHUB_REPO="HackSonTest"       # Repository name
```

## 2. Workflow Details (`.github/workflows/external-trigger.yml`)

This workflow supports two trigger types:

- `repository_dispatch`: triggered by the local server or any external system calling the GitHub REST API
- `workflow_dispatch`: manually triggered from the GitHub UI with a `message` input

The workflow prints:

- The event name (`github.event_name`)
- The `client_payload.message` from `repository_dispatch`
- Or `inputs.message` from `workflow_dispatch`

With this setup you get:

- A GitHub Action that can be called by external systems
- A simple `curl` example to demonstrate the full invocation flow

## 3. Call GitHub API Directly with curl (Without Local Server)

If you don’t want to use the local server, you can call GitHub’s `repository_dispatch` endpoint directly with `curl`.

**Prerequisite**: prepare the same environment variables (see step 1):

```bash
export GITHUB_TOKEN="<your_pat_here>"
export GITHUB_OWNER="rock-57blocks"
export GITHUB_REPO="HackSonTest"
```

### 3.1 Direct curl Call (Minimal Example)

```bash
curl -X POST \
	-H "Accept: application/vnd.github+json" \
	-H "Authorization: Bearer ${GITHUB_TOKEN}" \
	-H "X-GitHub-Api-Version: 2022-11-28" \
	"https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/dispatches" \
	-d '{
		"event_type": "run-external-job",
		"client_payload": {
			"message": "triggered directly by curl",
			"jira_ticket_url": "https://your-domain.atlassian.net/browse/KEY-123"
		}
	}'
```

Notes:

- `event_type` must match what the workflow listens to (`run-external-job` here).
- `client_payload.message` can be read in the workflow via `github.event.client_payload.message`.
- `client_payload.jira_ticket_url` is used to post a comment to that Jira ticket.

### 3.2 Wrap in a Shell Script (Optional)

You can also create a small script, e.g. `trigger_direct.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

MESSAGE="${1:-Hello from direct curl}"

curl -X POST \
	-H "Accept: application/vnd.github+json" \
	-H "Authorization: Bearer ${GITHUB_TOKEN}" \
	-H "X-GitHub-Api-Version: 2022-11-28" \
	"https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/dispatches" \
	-d "{\"event_type\": \"run-external-job\", \"client_payload\": {\"message\": \"${MESSAGE}\"}}"
```

Then:

```bash
chmod +x trigger_direct.sh
./trigger_direct.sh "message from direct curl"
```

This directly triggers the GitHub Action in the remote repository without relying on the local HTTP server.

