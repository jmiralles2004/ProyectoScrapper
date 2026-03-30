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
