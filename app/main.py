import subprocess
import sys

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "requests"])
    import requests as req_lib
else:
    import requests as req_lib

from flask import Flask, jsonify

app = Flask(__name__)

HINDSIGHT_BASE = "http://10.100.100.9:8888/v1/default/banks/openclaw-pip-main"

PROJECTS = {
    "structura-core": {
        "name": "STRUCTURA Core",
        "description": "Modular AI agent platform for resale — Pantheon methodology, Hindsight memory, client isolation",
        "next_steps": [
            "Complete client onboarding module",
            "Security audit & pen testing",
            "Package as Docker Compose stack"
        ],
        "tag": "project:structura-core",
        "href": "https://github.com/openclaw/openclaw"
    },
    "project-dashboard": {
        "name": "Project Dashboard",
        "description": "Real-time project tracking dashboard feeding from Hindsight memory into Homepage widgets",
        "next_steps": [
            "Add dynamic widget auto-refresh",
            "Implement project detail pages",
            "Clean up orphaned Docker containers"
        ],
        "tag": "project:project-dashboard",
        "href": "http://192.168.40.7:8889"
    },
    "hindsight-memory": {
        "name": "Hindsight Memory",
        "description": "Knowledge & memory platform — structured entity tracking, directives, and recall for AI agents",
        "next_steps": [
            "Migrate to local LLM with structured outputs",
            "Add observation deduplication",
            "Implement bank import/export"
        ],
        "tag": "project:hindsight-memory",
        "href": "http://10.100.100.9:8888/docs"
    },
    "pip-agent": {
        "name": "PiP Agent",
        "description": "AI household orchestrator — manages Pantheon sub-agents, home automation, and daily routines",
        "next_steps": [
            "Domovoi module implementation",
            "Home Assistant integration",
            "Automated morning briefing via Telegram"
        ],
        "tag": "project:pip-agent",
        "href": "https://docs.openclaw.ai"
    },
    "domovoi-module": {
        "name": "Domovoi Module",
        "description": "Home automation module for STRUCTURA — Home Assistant, family logistics, and smart home control",
        "next_steps": [
            "SPEC v1.0 completion",
            "Home Assistant API integration",
            "Family calendar sync"
        ],
        "tag": "project:domovoi-module",
        "href": None
    },
}

STATUS_MAP = {
    "active": "success",
    "in-progress": "warning",
    "planning": "info",
    "completed": "success",
    "abandoned": "danger",
    "on-hold": "danger",
}

def query_hindsight(project_tag):
    try:
        resp = req_lib.post(
            f"{HINDSIGHT_BASE}/memories/recall",
            json={"query": "project status progress owner", "tags": [project_tag], "tags_match": "any", "max_tokens": 500},
            timeout=10,
        )
        if resp.status_code == 200:
            for r in resp.json().get("results", []):
                metadata = r.get("metadata", {})
                if metadata.get("progress") or metadata.get("status"):
                    return metadata
        return {}
    except Exception as e:
        print(f"Hindsight query error: {e}")
        return {}

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "project-dashboard-api"})

@app.route("/projects/<project_id>", methods=["GET"])
def project_detail(project_id):
    project = PROJECTS.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    metadata = query_hindsight(project["tag"])
    return jsonify({"data": {
        "id": project_id,
        "name": project["name"],
        "description": project["description"],
        "next_steps": project["next_steps"],
        "status": metadata.get("status", "unknown"),
        "progress": int(metadata.get("progress", "0")),
        "owner": metadata.get("owner", "unknown"),
        "last_updated": metadata.get("last_updated", ""),
        "state": STATUS_MAP.get(metadata.get("status", ""), "info"),
        "href": project.get("href", ""),
    }})

@app.route("/projects", methods=["GET"])
def project_list():
    projects = []
    for pid, pinfo in PROJECTS.items():
        metadata = query_hindsight(pinfo["tag"])
        projects.append({
            "id": pid,
            "name": pinfo["name"],
            "description": pinfo["description"],
            "status": metadata.get("status", "unknown"),
            "progress": int(metadata.get("progress", "0")),
            "owner": metadata.get("owner", "unknown"),
            "state": STATUS_MAP.get(metadata.get("status", ""), "info"),
        })
    return jsonify({"data": projects})
