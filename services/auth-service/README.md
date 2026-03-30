# Auth Service - Phase 1

Servicio de autenticación para JobMatch.

## Qué incluye
- Registro de usuarios
- Login con JWT
- Endpoint protegido `/auth/me`
- Healthcheck en `/health`

## Ejecución local
```bash
cd services/auth-service
pip install -r requirements.txt
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
```

## Variables necesarias
- `DATABASE_URL`
- `JWT_SECRET`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

## Tests
```bash
pytest services/auth-service/tests -v
```
