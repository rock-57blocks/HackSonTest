import os
import json
from typing import Any, Dict

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_OWNER = os.environ.get("GITHUB_OWNER")
GITHUB_REPO = os.environ.get("GITHUB_REPO")


def github_config_ok() -> bool:
    return bool(GITHUB_TOKEN and GITHUB_OWNER and GITHUB_REPO)


@app.route("/health", methods=["GET"])
def health() -> Any:
    return {"status": "ok", "github_configured": github_config_ok()}


@app.route("/trigger", methods=["POST"])
def trigger() -> Any:
    if not github_config_ok():
        return (
            jsonify(
                {
                    "error": "Missing GitHub configuration. Set GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO.",
                }
            ),
            400,
        )

    try:
        data: Dict[str, Any] = request.get_json(force=True, silent=True) or {}
    except Exception:
        data = {}

    event_type = data.get("event_type", "run-external-job")
    message = data.get("message", "Hello from local server")

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "event_type": event_type,
        "client_payload": {"message": message},
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=10)

    if resp.status_code >= 400:
        return (
            jsonify(
                {
                    "error": "Failed to trigger repository_dispatch",
                    "status_code": resp.status_code,
                    "response": safe_json(resp),
                }
            ),
            500,
        )

    return jsonify({"status": "ok", "event_type": event_type, "message": message})


def safe_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return resp.text


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
