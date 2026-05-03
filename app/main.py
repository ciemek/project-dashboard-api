import subprocess
import sys

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "requests"])
    import requests as req_lib
else:
    import requests as req_lib

from flask import Flask, jsonify, render_template_string, request

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

STATUS_COLORS = {
    "active": "#22c55e",
    "in-progress": "#f59e0b",
    "planning": "#3b82f6",
    "completed": "#22c55e",
    "abandoned": "#ef4444",
    "on-hold": "#ef4444",
    "unknown": "#6b7280",
}

STATUS_LABELS = {
    "active": "Active",
    "in-progress": "In Progress",
    "planning": "Planning",
    "completed": "Completed",
    "abandoned": "Abandoned",
    "on-hold": "On Hold",
    "unknown": "Unknown",
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


def get_project_data(project_id):
    """Get project data with Hindsight metadata, used by both JSON and HTML views."""
    project = PROJECTS.get(project_id)
    if not project:
        return None
    metadata = query_hindsight(project["tag"])
    return {
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
    }


PROJECT_DETAIL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ project.name }} — STRUCTURA</title>
<style>
  :root {
    --bg: #0f172a;
    --card: #1e293b;
    --border: #334155;
    --text: #e2e8f0;
    --muted: #94a3b8;
    --accent: #3b82f6;
    --green: #22c55e;
    --yellow: #f59e0b;
    --red: #ef4444;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 2rem;
  }
  .container { max-width: 720px; margin: 0 auto; }

  /* Header */
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
  }
  .header h1 {
    font-size: 1.75rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .badge::before {
    content: '';
    width: 8px; height: 8px;
    border-radius: 50%;
    background: currentColor;
  }
  .badge-success { background: rgba(34,197,94,0.15); color: var(--green); }
  .badge-warning { background: rgba(245,158,11,0.15); color: var(--yellow); }
  .badge-danger  { background: rgba(239,68,68,0.15); color: var(--red); }
  .badge-info    { background: rgba(59,130,246,0.15); color: var(--accent); }

  /* Card */
  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
  }

  /* Description */
  .description {
    font-size: 1rem;
    line-height: 1.6;
    color: var(--muted);
  }

  /* Meta grid */
  .meta-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }
  .meta-item {
    text-align: center;
    padding: 1rem;
  }
  .meta-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    margin-bottom: 0.35rem;
  }
  .meta-value {
    font-size: 1.1rem;
    font-weight: 600;
  }

  /* Progress bar */
  .progress-wrap {
    margin: 1rem 0 0.25rem;
  }
  .progress-bar {
    width: 100%;
    height: 8px;
    background: var(--border);
    border-radius: 9999px;
    overflow: hidden;
  }
  .progress-fill {
    height: 100%;
    border-radius: 9999px;
    transition: width 0.6s ease;
  }
  .progress-text {
    font-size: 0.8rem;
    color: var(--muted);
    text-align: right;
    margin-top: 0.25rem;
  }

  /* Next steps */
  .next-steps-title {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
    margin-bottom: 0.75rem;
  }
  .step {
    display: flex;
    align-items: flex-start;
    gap: 0.65rem;
    padding: 0.5rem 0;
  }
  .step-icon {
    width: 20px; height: 20px;
    border-radius: 50%;
    border: 2px solid var(--border);
    flex-shrink: 0;
    margin-top: 2px;
  }
  .step-text {
    font-size: 0.9rem;
    line-height: 1.4;
  }

  /* Link */
  .link-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1rem;
    border-radius: 0.5rem;
    background: rgba(59,130,246,0.08);
    border: 1px solid rgba(59,130,246,0.2);
    text-decoration: none;
    color: var(--accent);
    font-size: 0.9rem;
    font-weight: 500;
    transition: background 0.2s;
  }
  .link-card:hover { background: rgba(59,130,246,0.15); }
  .link-arrow { font-size: 1.1rem; }

  /* Back link */
  .back {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--muted);
    text-decoration: none;
    font-size: 0.85rem;
    margin-bottom: 1.25rem;
    transition: color 0.2s;
  }
  .back:hover { color: var(--text); }

  /* Responsive */
  @media (max-width: 480px) {
    .meta-grid { grid-template-columns: 1fr; }
    body { padding: 1rem; }
  }
</style>
</head>
<body>
<div class="container">

  <a href="/projects" class="back">← All Projects</a>

  <div class="header">
    <h1>{{ project.name }}</h1>
    <span class="badge badge-{{ project.state }}">{{ status_label }}</span>
  </div>

  <div class="card">
    <p class="description">{{ project.description }}</p>

    <div class="progress-wrap">
      <div class="progress-bar">
        <div class="progress-fill" style="width: {{ project.progress }}%; background: {{ progress_color }}"></div>
      </div>
      <div class="progress-text">{{ project.progress }}% complete</div>
    </div>

    <div class="meta-grid" style="margin-top:1.25rem">
      <div class="meta-item">
        <div class="meta-label">Owner</div>
        <div class="meta-value">{{ project.owner }}</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Status</div>
        <div class="meta-value" style="color:{{ status_hex }}">{{ status_label }}</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Updated</div>
        <div class="meta-value">{{ project.last_updated or '—' }}</div>
      </div>
    </div>
  </div>

  {% if project.next_steps %}
  <div class="card">
    <div class="next-steps-title">Next Steps</div>
    {% for step in project.next_steps %}
    <div class="step">
      <div class="step-icon"></div>
      <div class="step-text">{{ step }}</div>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  {% if project.href %}
  <a href="{{ project.href }}" target="_blank" class="link-card">
    <span>Open project link</span>
    <span class="link-arrow">→</span>
  </a>
  {% endif %}

</div>
</body>
</html>"""

PROJECT_LIST_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>STRUCTURA Projects</title>
<style>
  :root {
    --bg: #0f172a;
    --card: #1e293b;
    --border: #334155;
    --text: #e2e8f0;
    --muted: #94a3b8;
    --accent: #3b82f6;
    --green: #22c55e;
    --yellow: #f59e0b;
    --red: #ef4444;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 2rem;
  }
  .container { max-width: 720px; margin: 0 auto; }
  h1 { font-size: 1.5rem; font-weight: 700; margin-bottom: 1.25rem; }

  .project-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 0.75rem;
    padding: 1.25rem;
    margin-bottom: 0.85rem;
    text-decoration: none;
    color: var(--text);
    display: block;
    transition: border-color 0.2s, transform 0.15s;
  }
  .project-card:hover {
    border-color: var(--accent);
    transform: translateY(-1px);
  }
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
  }
  .card-name { font-size: 1.05rem; font-weight: 600; }
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.2rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .badge::before {
    content: '';
    width: 7px; height: 7px;
    border-radius: 50%;
    background: currentColor;
  }
  .badge-success { background: rgba(34,197,94,0.15); color: var(--green); }
  .badge-warning { background: rgba(245,158,11,0.15); color: var(--yellow); }
  .badge-danger  { background: rgba(239,68,68,0.15); color: var(--red); }
  .badge-info    { background: rgba(59,130,246,0.15); color: var(--accent); }

  .card-desc {
    font-size: 0.85rem;
    color: var(--muted);
    line-height: 1.4;
    margin-bottom: 0.75rem;
  }

  .card-meta {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    font-size: 0.8rem;
    color: var(--muted);
  }
  .card-meta span { display: flex; align-items: center; gap: 0.3rem; }

  .progress-mini {
    width: 60px; height: 5px;
    background: var(--border);
    border-radius: 9999px;
    overflow: hidden;
  }
  .progress-mini-fill {
    height: 100%;
    border-radius: 9999px;
  }
</style>
</head>
<body>
<div class="container">
  <h1>STRUCTURA Projects</h1>
  {% for p in projects %}
  <a href="/projects/{{ p.id }}/view" class="project-card">
    <div class="card-header">
      <span class="card-name">{{ p.name }}</span>
      <span class="badge badge-{{ p.state }}">{{ p.status_label }}</span>
    </div>
    <div class="card-desc">{{ p.description }}</div>
    <div class="card-meta">
      <span>
        <div class="progress-mini"><div class="progress-mini-fill" style="width:{{ p.progress }}%;background:{{ p.progress_color }}"></div></div>
        {{ p.progress }}%
      </span>
      <span>👤 {{ p.owner }}</span>
    </div>
  </a>
  {% endfor %}
</div>
</body>
</html>"""


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "project-dashboard-api"})


@app.route("/projects/<project_id>", methods=["GET"])
def project_detail(project_id):
    """JSON API endpoint (for Homepage customapi widgets)."""
    data = get_project_data(project_id)
    if not data:
        return jsonify({"error": "Project not found"}), 404
    return jsonify({"data": data})


@app.route("/projects/<project_id>/view", methods=["GET"])
def project_detail_html(project_id):
    """HTML page for project detail (for clicking through from Homepage)."""
    data = get_project_data(project_id)
    if not data:
        return "<h1>404 — Project not found</h1>", 404

    status_label = STATUS_LABELS.get(data["status"], "Unknown")
    status_hex = STATUS_COLORS.get(data["status"], "#6b7280")

    # Progress bar color: green > 60, yellow > 30, red otherwise
    if data["progress"] >= 60:
        progress_color = "#22c55e"
    elif data["progress"] >= 30:
        progress_color = "#f59e0b"
    else:
        progress_color = "#3b82f6"

    return render_template_string(
        PROJECT_DETAIL_HTML,
        project=data,
        status_label=status_label,
        status_hex=status_hex,
        progress_color=progress_color,
    )


@app.route("/projects", methods=["GET"])
def project_list():
    """JSON API endpoint (list all projects)."""
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


@app.route("/projects/view", methods=["GET"])
def project_list_html():
    """HTML page listing all projects."""
    projects = []
    for pid, pinfo in PROJECTS.items():
        metadata = query_hindsight(pinfo["tag"])
        status = metadata.get("status", "unknown")
        progress = int(metadata.get("progress", "0"))
        projects.append({
            "id": pid,
            "name": pinfo["name"],
            "description": pinfo["description"],
            "status": status,
            "status_label": STATUS_LABELS.get(status, "Unknown"),
            "progress": progress,
            "progress_color": "#22c55e" if progress >= 60 else "#f59e0b" if progress >= 30 else "#3b82f6",
            "owner": metadata.get("owner", "unknown"),
            "state": STATUS_MAP.get(status, "info"),
        })
    return render_template_string(PROJECT_LIST_HTML, projects=projects)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8889)