# Criterios de aceptacion - Fase 6

- El servicio `integration-service` arranca con Docker.
- `GET /integration/health` responde con `200`.
- `POST /integration/offers/import` importa ofertas con vectores externos.
- `POST /integration/profiles/import-vector` guarda vectores de perfil.
- `GET /integration/offers/catalog` devuelve ofertas de la base vectorial.
- `GET /integration/offers/recommended` requiere JWT y devuelve ranking.
- Se aplica API key interna en ingesta cuando esta configurada.
- Qdrant almacena colecciones de perfiles y ofertas.
- Nginx expone correctamente rutas `/integration/*`.
- Los tests de `integration-service` pasan.
- Las suites activas de `auth-service`, `profile-service` e `integration-service` pasan por ruta.
- Las suites de backup de Fase 1, Fase 2 y Fase 6 pasan por ruta.
- El smoke test `scripts/phase6_smoke_test.sh` pasa con datos simulados.
- Queda documentado que unit tests usan persistencia fake en memoria y smoke test usa persistencia real en Qdrant.
- Existe script de limpieza total de artefactos fake: `scripts/cleanup_fake_phase6_data.sh`.
- Quedan documentados endpoints recomendados para frontend como backlog (sin declararlos implementados).
