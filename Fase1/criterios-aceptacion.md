# Criterios de aceptación - Fase 1

- El servicio `auth-service` arranca con Docker.
- `GET /health` responde con `200`.
- `POST /auth/register` crea usuarios en PostgreSQL.
- `POST /auth/login` devuelve un JWT válido.
- `GET /auth/me` funciona con `Authorization: Bearer <token>`.
- Nginx expone las rutas `/auth/*`.
- Los tests de autenticación pasan.
