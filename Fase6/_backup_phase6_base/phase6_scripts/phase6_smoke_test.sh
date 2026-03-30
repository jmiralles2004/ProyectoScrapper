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

PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

echo "[INFO] Levantando qdrant + integration-service para smoke test..."
cd "$ROOT_DIR"
docker compose --env-file "$ENV_FILE" up -d qdrant integration-service >/dev/null

echo "[INFO] Ejecutando smoke test con datos simulados..."
PHASE6_ENV_FILE="$ENV_FILE" "$PYTHON_BIN" - <<'PY'
import json
import os
import time
import uuid
from pathlib import Path

import httpx
import jwt


def load_env_file(path: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


env_path = os.environ["PHASE6_ENV_FILE"]
env_values = load_env_file(env_path)

base_port = int(env_values.get("INTEGRATION_SERVICE_PORT", "8002"))
base_url = f"http://localhost:{base_port}"
vector_size = int(env_values.get("INTEGRATION_VECTOR_SIZE", "384"))
jwt_secret = env_values.get("JWT_SECRET", "")
internal_key = env_values.get("INTEGRATION_INGEST_API_KEY", "")

if not jwt_secret:
    raise SystemExit("[ERROR] JWT_SECRET vacio en entorno")


def build_vector(seed: int, size: int) -> list[float]:
    return [((seed + idx) % 10) / 10.0 for idx in range(size)]


for _ in range(30):
    try:
        health = httpx.get(f"{base_url}/health", timeout=2)
        if health.status_code == 200:
            break
    except Exception:
        pass
    time.sleep(1)
else:
    raise SystemExit("[ERROR] integration-service no esta listo")

headers_ingest: dict[str, str] = {}
if internal_key:
    headers_ingest["x-internal-api-key"] = internal_key

user_id = str(uuid.uuid4())

offers_payload = {
    "offers": [
        {
            "offer_id": "smoke-offer-1",
            "title": "Backend Developer TEST",
            "company": "FakeCorp",
            "description": "Oferta simulada para smoke test",
            "location": "Madrid",
            "apply_url": "https://example.test/apply/1",
            "vector": build_vector(1, vector_size),
            "metadata": {"source": "smoke-test", "fake_data": True},
        },
        {
            "offer_id": "smoke-offer-2",
            "title": "Data Engineer TEST",
            "company": "FakeCorp",
            "description": "Otra oferta simulada para smoke test",
            "location": "Barcelona",
            "apply_url": "https://example.test/apply/2",
            "vector": build_vector(3, vector_size),
            "metadata": {"source": "smoke-test", "fake_data": True},
        },
    ]
}

import_offers = httpx.post(
    f"{base_url}/integration/offers/import",
    json=offers_payload,
    headers=headers_ingest,
    timeout=20,
)
if import_offers.status_code != 201:
    raise SystemExit(f"[ERROR] import_offers fallo: {import_offers.status_code} {import_offers.text}")

profile_payload = {
    "user_id": user_id,
    "vector": build_vector(1, vector_size),
    "metadata": {"source": "smoke-test", "fake_data": True},
}
import_profile = httpx.post(
    f"{base_url}/integration/profiles/import-vector",
    json=profile_payload,
    headers=headers_ingest,
    timeout=20,
)
if import_profile.status_code != 201:
    raise SystemExit(f"[ERROR] import_profile fallo: {import_profile.status_code} {import_profile.text}")

catalog = httpx.get(
    f"{base_url}/integration/offers/catalog",
    params={"limit": 10},
    headers=headers_ingest,
    timeout=20,
)
if catalog.status_code != 200:
    raise SystemExit(f"[ERROR] catalog fallo: {catalog.status_code} {catalog.text}")

token = jwt.encode(
    {
        "sub": user_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    },
    jwt_secret,
    algorithm=env_values.get("JWT_ALGORITHM", "HS256"),
)

recommended = httpx.get(
    f"{base_url}/integration/offers/recommended",
    headers={"Authorization": f"Bearer {token}"},
    params={"limit": 10},
    timeout=20,
)
if recommended.status_code != 200:
    raise SystemExit(f"[ERROR] recommended fallo: {recommended.status_code} {recommended.text}")

summary = {
    "note": "Datos simulados/falsos para validar comportamiento tecnico",
    "health": health.json(),
    "import_offers": import_offers.json(),
    "import_profile": import_profile.json(),
    "catalog_total": catalog.json().get("total"),
    "recommended_total": recommended.json().get("total"),
    "top_offer": (recommended.json().get("offers") or [{}])[0].get("offer_id"),
    "user_id": user_id,
}

summary_path = Path("/tmp/phase6-smoke-summary.json")
summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(summary, indent=2, ensure_ascii=False))
print(f"[INFO] Resumen guardado en {summary_path}")
PY

echo "[OK] Smoke test de Fase 6 completado."
