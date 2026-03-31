#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_ENV_FILE="$ROOT_DIR/.env.docker"

if [[ -n "${ENV_FILE:-}" ]]; then
  RESOLVED_ENV_FILE="$ENV_FILE"
elif [[ -f "$DEFAULT_ENV_FILE" ]]; then
  RESOLVED_ENV_FILE="$DEFAULT_ENV_FILE"
else
  RESOLVED_ENV_FILE="$ROOT_DIR/.env"
fi

if [[ ! -f "$RESOLVED_ENV_FILE" ]]; then
  echo "[ERROR] No existe ENV_FILE: $RESOLVED_ENV_FILE" >&2
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

echo "[INFO] Levantando stack completo con Docker Compose..."
cd "$ROOT_DIR"
docker compose --env-file "$RESOLVED_ENV_FILE" up -d --build >/dev/null

echo "[INFO] Ejecutando validacion integral de endpoints..."
PHASE8_ENV_FILE="$RESOLVED_ENV_FILE" "$PYTHON_BIN" - <<'PY'
import json
import os
import time
import uuid
from pathlib import Path

import httpx


def load_env_file(path: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def build_test_pdf_bytes() -> bytes:
    content_stream = "BT\n/F1 18 Tf\n50 100 Td\n(JobMatch CV Test) Tj\nET\n"
    content_bytes = content_stream.encode("latin-1")

    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        f"<< /Length {len(content_bytes)} >>\nstream\n{content_stream}endstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]

    for i, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{i} 0 obj\n".encode("latin-1"))
        pdf.extend(obj.encode("latin-1"))
        pdf.extend(b"\nendobj\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)+1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf.extend(f"{off:010d} 00000 n \n".encode("latin-1"))

    pdf.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\n".encode("latin-1"))
    pdf.extend(f"startxref\n{xref_start}\n%%EOF\n".encode("latin-1"))
    return bytes(pdf)


def ensure_status(response: httpx.Response, expected: int, label: str) -> None:
    if response.status_code != expected:
        raise SystemExit(
            f"[ERROR] {label}: esperado={expected} recibido={response.status_code} body={response.text}"
        )
    print(f"[OK] {label}")


def wait_for_health(client: httpx.Client, base_url: str, timeout_seconds: int = 60) -> None:
    started = time.time()
    while time.time() - started < timeout_seconds:
        try:
            response = client.get(f"{base_url}/health")
            if response.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(1)
    raise SystemExit("[ERROR] Nginx /health no responde 200 dentro del timeout")


env_values = load_env_file(os.environ["PHASE8_ENV_FILE"])
nginx_port = int(env_values.get("NGINX_PORT", "80"))
auth_port = int(env_values.get("AUTH_SERVICE_PORT", "8000"))
profile_port = int(env_values.get("PROFILE_SERVICE_PORT", "8001"))
integration_port = int(env_values.get("INTEGRATION_SERVICE_PORT", "8002"))
vector_size = int(env_values.get("INTEGRATION_VECTOR_SIZE", "384"))
integration_ingest_api_key = env_values.get("INTEGRATION_INGEST_API_KEY", "").strip()

base_url = f"http://localhost:{nginx_port}"
auth_direct = f"http://localhost:{auth_port}"
profile_direct = f"http://localhost:{profile_port}"
integration_direct = f"http://localhost:{integration_port}"

client = httpx.Client(timeout=30)
wait_for_health(client, base_url)

# Infra y salud
ensure_status(client.get(f"{base_url}/health"), 200, "Nginx health")
ensure_status(client.get(f"{base_url}/auth/health"), 200, "Auth health por gateway")
ensure_status(client.get(f"{base_url}/profiles/health"), 200, "Profile health por gateway")
ensure_status(client.get(f"{base_url}/integration/health"), 200, "Integration health por gateway")

# Documentacion
auth_docs = client.get(f"{base_url}/auth/docs")
ensure_status(auth_docs, 200, "Auth Swagger")
if "Swagger UI" not in auth_docs.text:
    raise SystemExit("[ERROR] Auth Swagger no devuelve HTML esperado")
print("[OK] Auth Swagger devuelve HTML")

ensure_status(client.get(f"{base_url}/auth/openapi.json"), 200, "Auth OpenAPI")
ensure_status(client.get(f"{base_url}/profiles/docs"), 200, "Profiles Swagger")
ensure_status(client.get(f"{base_url}/profiles/openapi.json"), 200, "Profiles OpenAPI")
ensure_status(client.get(f"{base_url}/integration/docs"), 200, "Integration Swagger")
ensure_status(client.get(f"{base_url}/integration/openapi.json"), 200, "Integration OpenAPI")

swagger_redirect = client.get(f"{base_url}/swagger", follow_redirects=False)
ensure_status(swagger_redirect, 308, "Redirect /swagger -> /swagger/")
ensure_status(client.get(f"{base_url}/swagger/"), 200, "Swagger UI unificado")

# Health directos
ensure_status(client.get(f"{auth_direct}/health"), 200, "Auth /health directo")
ensure_status(client.get(f"{profile_direct}/health"), 200, "Profile /health directo")
ensure_status(client.get(f"{integration_direct}/health"), 200, "Integration /health directo")

# Auth flow
email = f"e2e_{uuid.uuid4().hex[:10]}@example.com"
password = "secret1234"

register_response = client.post(
    f"{base_url}/auth/register",
    json={"email": email, "password": password},
)
ensure_status(register_response, 201, "Auth register")
user_id = register_response.json()["id"]

login_response = client.post(
    f"{base_url}/auth/login",
    json={"email": email, "password": password},
)
ensure_status(login_response, 200, "Auth login")
token = login_response.json()["access_token"]
auth_headers = {"Authorization": f"Bearer {token}"}

ensure_status(client.get(f"{base_url}/auth/me", headers=auth_headers), 200, "Auth me")

# Profile flow
pdf_bytes = build_test_pdf_bytes()
profile_upload = client.post(
    f"{base_url}/profiles/cv",
    headers=auth_headers,
    files={"file": ("cv_test.pdf", pdf_bytes, "application/pdf")},
)
ensure_status(profile_upload, 201, "Profile upload CV")

career_goal_payload = {
    "desired_role": "Arquitecto",
    "transition_summary": "Experiencia previa en hosteleria y transicion activa al sector de arquitectura",
}
career_goal_response = client.put(
    f"{base_url}/profiles/career-goals",
    headers=auth_headers,
    json=career_goal_payload,
)
ensure_status(career_goal_response, 200, "Profile career goal upsert")

profile_me_response = client.get(f"{base_url}/profiles/me", headers=auth_headers)
ensure_status(profile_me_response, 200, "Profile me")
if profile_me_response.json().get("desired_role") != "Arquitecto":
    raise SystemExit("[ERROR] Profile me no refleja desired_role esperado")
print("[OK] Profile me refleja desired_role")

# Integration flow
ingest_headers: dict[str, str] = {}
if integration_ingest_api_key:
    ingest_headers["x-internal-api-key"] = integration_ingest_api_key

vector = [round(0.001 * ((idx % 100) + 1), 6) for idx in range(vector_size)]
offers_payload = {
    "offers": [
        {
            "offer_id": f"offer-e2e-{uuid.uuid4().hex[:8]}",
            "title": "Backend Developer E2E",
            "company": "JobMatch Labs",
            "description": "Oferta de prueba integral de endpoints",
            "location": "Remote",
            "apply_url": "https://example.com/apply/e2e",
            "vector": vector,
            "metadata": {"source": "phase8-e2e"},
        }
    ]
}

profile_vector_payload = {
    "user_id": user_id,
    "vector": vector,
    "metadata": {"source": "phase8-e2e"},
}

ensure_status(
    client.post(
        f"{base_url}/integration/offers/import",
        json=offers_payload,
        headers=ingest_headers,
    ),
    201,
    "Integration offers import",
)

ensure_status(
    client.post(
        f"{base_url}/integration/profiles/import-vector",
        json=profile_vector_payload,
        headers=ingest_headers,
    ),
    201,
    "Integration profile vector import",
)

catalog_response = client.get(
    f"{base_url}/integration/offers/catalog",
    params={"limit": 10},
    headers=ingest_headers,
)
ensure_status(catalog_response, 200, "Integration offers catalog")
if catalog_response.json().get("total", 0) < 1:
    raise SystemExit("[ERROR] Integration catalog devolvio total < 1")
print("[OK] Integration catalog tiene resultados")

recommended_response: httpx.Response | None = None
for _ in range(10):
    recommended_response = client.get(
        f"{base_url}/integration/offers/recommended",
        params={"limit": 10},
        headers=auth_headers,
    )
    if recommended_response.status_code == 200:
        break
    time.sleep(1)

if recommended_response is None:
    raise SystemExit("[ERROR] No se pudo obtener respuesta de recommended")
ensure_status(recommended_response, 200, "Integration recommended")
if recommended_response.json().get("total", 0) < 1:
    raise SystemExit("[ERROR] Integration recommended devolvio total < 1")
print("[OK] Integration recommended tiene resultados")

summary = {
    "note": "Validacion integral de endpoints completada con datos simulados",
    "base_url": base_url,
    "user_id": user_id,
    "catalog_total": catalog_response.json().get("total"),
    "recommended_total": recommended_response.json().get("total"),
}
summary_path = Path("/tmp/phase8-endpoints-e2e-summary.json")
summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

print("\n===== RESULTADO FINAL =====")
print("Todos los endpoints probados funcionan correctamente.")
print(f"[INFO] Resumen guardado en {summary_path}")
PY

echo "[OK] Validacion integral completada."
