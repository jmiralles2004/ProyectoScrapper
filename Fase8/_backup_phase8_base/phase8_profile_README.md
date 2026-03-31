# Profile Service (Fase 2)

Servicio FastAPI para gestionar perfiles y CVs en PDF, incluyendo OCR para CVs escaneados.

## Endpoints
- `GET /health`
- `GET /profiles/health`
- `POST /profiles/cv` (requiere JWT Bearer, admite formulario opcional de cambio profesional)
- `PUT /profiles/career-goals` (requiere JWT Bearer)
- `GET /profiles/me` (requiere JWT Bearer)

## Variables de entorno mínimas
- `DATABASE_URL`
- `JWT_SECRET`
- `JWT_ALGORITHM`
- `MINIO_ENDPOINT`
- `MINIO_ROOT_USER`
- `MINIO_ROOT_PASSWORD`
- `MINIO_BUCKET_PROFILES`
- `OCR_ENABLED`
- `OCR_LANGUAGES`
- `OCR_DPI`

## OCR (PDF escaneados)
- Si el PDF no tiene texto embebido, el servicio aplica OCR automáticamente.
- Por defecto usa `spa+eng` para mejorar resultados en CVs mixtos.

## Formato del JSON guardado en MinIO
El objeto guardado en MinIO no es solo texto plano; ahora se guarda un sobre ETL:
- `version`: versión del formato (`phase2-etl-v1`)
- `career_goal`: objetivo profesional declarado (`desired_role`, `transition_summary`)
- `extraction`: método usado (`embedded` u `ocr`) y métricas de longitud
- `raw.cv_text`: texto bruto extraído
- `normalized.cv_text`: texto normalizado
- `normalized.sections`: bloques detectados (contact, experience, education, etc.)
- `normalized.entities`: emails, teléfonos y enlaces detectados
- `quality`: score y señales para revisión manual

## Ejecutar local
```bash
uvicorn app.main:create_app --factory --reload --port 8001
```

## Tests
```bash
pytest tests/test_profiles.py -v
```
