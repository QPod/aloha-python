#!/bin/bash
set -euo pipefail

ACTION="${1:-up}"

USERNAME="$(whoami)"
USERID="$(id -u)"


BASE_APP_PORT=40000
BASE_WEB_PORT=43000
export PORT_APP=$((BASE_APP_PORT + USERID))
export PORT_WEB=$((BASE_WEB_PORT + USERID))
export PROJECT_NAME="dev-app-demo-${USERNAME}"
export CONTAINER_NAME="dev-app-demo-${USERNAME}"


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

shopt -s nullglob
FILES=("$SCRIPT_DIR"/docker-compose.*.DEV.yml)
if [ ${#FILES[@]} -eq 0 ]; then
  echo "❌ No docker-compose.*.DEV.yml found in $SCRIPT_DIR"
  exit 1
fi
COMPOSE="${FILES[0]}"

# ---------- Port checking function ----------
check_port() {
  local port=$1
  if ss -lnt | awk '{print $4}' | grep -q ":$port$"; then
    echo "❌ ERROR: Port $port is already in use. Aborting."
    exit 1
  fi
}

require_ports_free() {
  echo "🔍 Checking port availability..."
  check_port "$PORT_APP"
  check_port "$PORT_WEB"
  echo "✅ Ports available."
}

# ---------- Action Dispatcher ----------
echo "----------------------------------------"
echo "User:            $USERNAME (UID: $USERID)"
echo "Project Name:    $PROJECT_NAME"
echo "Container:       $CONTAINER_NAME"
echo "App Port Expose: $PORT_APP"
echo "Web Port Expose: $PORT_WEB"
echo "Action:          $ACTION"
echo "Compose:         $COMPOSE"
echo "----------------------------------------"


case "$ACTION" in
  up)
    require_ports_free
    docker-compose -f "$COMPOSE" -p "$PROJECT_NAME" up -d
    echo "✅ Development environment launched."
    ;;
  restart)
    require_ports_free
    docker-compose -f "$COMPOSE" -p "$PROJECT_NAME" restart
    echo "🔁 Restart completed."
    ;;
  down)
    docker-compose -f "$COMPOSE" -p "$PROJECT_NAME" down
    echo "🛑 Environment stopped."
    ;;
  enter)
    echo "↩️ Entering into development container:"
    docker exec -it $CONTAINER_NAME bash
    ;;
  logs)
    echo "🕵 Attach to container for log inspection:"
    docker-compose -f "$COMPOSE" -p "$PROJECT_NAME" logs -f
    ;;
  *)
    echo "Usage: $0 [up|down|restart|logs]"
    exit 1
    ;;
esac
