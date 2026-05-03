#!/bin/bash
# Deploy project-dashboard-api on Unraid via UnraidClaw API
# Usage: ./deploy-unraid.sh [API_KEY] [UNRAID_HOST]

API_KEY="${1:-dc0a4881f1bc8b9dc46a524bd3ddb875c1b9f2818171dc15d8096954689b5436}"
HOST="${2:-192.168.40.7:9876}"
IMAGE="ghcr.io/ciemek/project-dashboard-api:latest"
CONTAINER_NAME="structura-dashboard-api"

echo "Deploying $CONTAINER_NAME on Unraid..."

# Stop and remove existing container
for cid in $(curl -sk -H "X-API-Key: $API_KEY" "https://$HOST/api/docker/containers" | python3 -c "import sys,json; [print(c['id']) for c in json.load(sys.stdin).get('data',json.load(sys.stdin)) if c.get('names',c.get('name','')) == '$CONTAINER_NAME' or '$CONTAINER_NAME' in c.get('names',[])]" 2>/dev/null); do
  echo "Stopping $cid..."
  curl -sk -X POST -H "X-API-Key: $API_KEY" "https://$HOST/api/docker/containers/$cid/stop" >/dev/null 2>&1
  sleep 2
  echo "Removing $cid..."
  curl -sk -X DELETE -H "X-API-Key: $API_KEY" "https://$HOST/api/docker/containers/$cid" >/dev/null 2>&1
  sleep 2
done

# Create new container
echo "Creating container..."
curl -sk -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  "https://$HOST/api/docker/containers" \
  -d "{
    \"image\": \"$IMAGE\",
    \"name\": \"$CONTAINER_NAME\",
    \"env\": [\"TZ=Europe/Warsaw\", \"PORT=8889\"],
    \"restart\": \"unless-stopped\",
    \"network\": \"host\",
    \"webui\": \"http://[IP]:8889\"
  }" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Container ID: {d.get(\"data\",d).get(\"id\",\"ERROR\")}')"

echo ""
echo "Waiting for container to start..."
sleep 10

echo "Health check:"
curl -sk http://192.168.40.7:8889/health 2>/dev/null || echo "Container not responding yet (may still be pulling image)"
