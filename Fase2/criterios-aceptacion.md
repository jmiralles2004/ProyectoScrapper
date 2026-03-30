# Criterios de aceptación - Fase 2

- El servicio `profile-service` arranca con Docker.
- `GET /profiles/health` responde con `200`.
- `POST /profiles/cv` acepta PDF con `Authorization: Bearer <token>`.
- `POST /profiles/cv` procesa PDFs escaneados usando OCR cuando no hay texto embebido.
- El JSON en MinIO incluye estructura ETL (`raw`, `normalized`, `quality`).
- El texto extraído del CV se guarda en PostgreSQL (`profiles`).
- El JSON del perfil se guarda en MinIO (bucket `profiles`).
- `GET /profiles/me` devuelve el perfil del usuario autenticado.
- Nginx expone las rutas `/profiles/*`.
- Los tests de `profile-service` pasan.
