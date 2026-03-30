#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env.docker}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[ERROR] No existe ENV_FILE: $ENV_FILE" >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] docker no esta disponible en PATH" >&2
  exit 1
fi

cd "$ROOT_DIR"

echo "[WARN] Este script elimina datos de prueba/simulados de Fase 6 y recursos Docker del proyecto."
echo "[INFO] Bajando stack Docker del proyecto y eliminando volumenes..."
docker compose --env-file "$ENV_FILE" down -v --remove-orphans || true

echo "[INFO] Eliminando caches/artefactos locales de pruebas..."
rm -rf "$ROOT_DIR/.pytest_cache"
find "$ROOT_DIR/services/integration-service" -type d -name "__pycache__" -prune -exec rm -rf {} +
find "$ROOT_DIR/Fase6" -type d -name "__pycache__" -prune -exec rm -rf {} +
rm -f /tmp/phase6-smoke-summary.json
rm -f /tmp/phase6-smoke-*.json

echo "[INFO] Limpieza completada."
echo "[INFO] Si quieres volver a validar, ejecuta: scripts/phase6_smoke_test.sh"
