#!/usr/bin/env bash
set -euo pipefail

# Stops and removes all docker containers on the host after a confirmation prompt.
# Safe to run from bash on Windows (Git Bash / WSL) or any Unix-like shell.

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found in PATH. Install Docker or run this from a machine with Docker." >&2
  exit 1
fi

all_containers=$(docker ps -aq)
if [ -z "$all_containers" ]; then
  echo "No Docker containers found. Nothing to do."
  exit 0
fi

echo "The following containers will be stopped and removed:"
docker ps -a --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"

read -r -p "Are you sure you want to STOP and REMOVE all containers? [y/N]: " confirm
case "$confirm" in
  [yY]|[yY][eE][sS])
    ;;
  *)
    echo "Cancelled by user. No containers were removed."
    exit 0
    ;;
esac

echo "Stopping containers..."
docker stop $all_containers || true

echo "Removing containers (and anonymous volumes)..."
docker rm -v $all_containers || true

echo "All done."
