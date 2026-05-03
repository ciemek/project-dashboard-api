# STRUCTURA Project Dashboard API

Flask middleware between [Homepage](https://gethomepage.dev/) custom API widgets and [Hindsight](https://hindsight.vectorize.io/) memory platform.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /projects` | List all projects with status |
| `GET /projects/<id>` | Project detail with description & next steps |

## Project IDs

- `structura-core` — Modular AI agent platform
- `project-dashboard` — Project tracking dashboard
- `hindsight-memory` — Knowledge & memory platform
- `pip-agent` — AI assistant & orchestrator
- `domovoi-module` — Home automation module

## Docker Deployment (Unraid)

```bash
# Build and push
docker build -t ciemek/project-dashboard-api:latest .
docker push ciemek/project-dashboard-api:latest

# Or deploy via Unraid (use image name: ciemek/project-dashboard-api:latest)
# Volume mount: /mnt/user/ai_workspace/structura-api:/app/app (optional, for live code updates)
# Network: host
# Port: 8889
```

## Homepage Integration

Add to `services.yaml`:

```yaml
- STRUCTURA Projects:
  - STRUCTURA Core:
      icon: mdi-clipboard-list-outline
      description: Modular AI agent platform
      href: http://192.168.40.7:8889/projects/structura-core
      widget:
        type: customapi
        url: http://192.168.40.7:8889/projects/structura-core
        method: GET
        mappings:
          - field: data.status
            label: Status
            format: text
          - field: data.progress
            label: Progress
            format: percent
          - field: data.owner
            label: Owner
            format: text
```

## Configuration

Environment variables:
- `HINDSIGHT_BASE` — Hindsight API URL (default: `http://10.100.100.9:8888/v1/default/banks/openclaw-pip-main`)
- `PORT` — Server port (default: `8889`)

## License

MIT
