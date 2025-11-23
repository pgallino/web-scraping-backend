#!/usr/bin/env bash
set -euo pipefail

# Levanta los contenedores definidos en docker-compose.dev.yml
# y entra a la shell del servicio especificado (por defecto: api).
# Uso: ./scripts/start_and_shell.sh [servicio] [shell]
# Ejemplo: ./scripts/start_and_shell.sh api sh

COMPOSE_FILE="docker-compose.dev.yml"
SERVICE="${1:-api}"
SHELL_CMD="${2:-sh}"

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "No se encontró '$COMPOSE_FILE' en $(pwd). Asegúrate de ejecutar desde la raíz del proyecto."
  exit 1
fi

echo "Construyendo y levantando contenedores (archivo: $COMPOSE_FILE)..."
docker compose -f "$COMPOSE_FILE" up -d --build

echo "Esperando un momento para que los servicios inicien..."
sleep 1

echo "Abriendo shell en el servicio '$SERVICE' (shell: $SHELL_CMD)."
docker compose -f "$COMPOSE_FILE" exec "$SERVICE" "$SHELL_CMD"
