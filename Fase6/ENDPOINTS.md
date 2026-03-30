# Endpoints - Fase 6

## Fase 6 - Integration Service

| Metodo | Ruta | Servicio | Descripcion |
|--------|------|---------|-------------|
| `GET` | `/integration/health` | Integration Service | Comprueba que el servicio esta operativo |
| `POST` | `/integration/offers/import` | Integration Service | Importa lote de ofertas con sus vectores |
| `POST` | `/integration/profiles/import-vector` | Integration Service | Importa vector de perfil de un usuario |
| `GET` | `/integration/offers/catalog` | Integration Service | Lista catalogo de ofertas almacenadas |
| `GET` | `/integration/offers/recommended` | Integration Service | Devuelve ofertas recomendadas para el usuario autenticado |

## Uso
Los endpoints se consumen a traves de Nginx en `/integration/*`.
La base vectorial es Qdrant y el ranking se calcula por similitud de vectores.

## Nota de pruebas
- Los ejemplos y payloads de esta fase usan datos simulados/falsos.
- Son unicamente para smoke test tecnico y validacion de comportamiento.
- No representan datos reales de negocio ni calidad real de matching.

## Validacion de test y persistencia

- `services/auth-service/tests`: persistencia fake en memoria.
- `services/profile-service/tests`: persistencia fake en memoria (repo + storage).
- `services/integration-service/tests`: persistencia fake en memoria (vector store).
- `scripts/phase6_smoke_test.sh`: persistencia real en Qdrant con datos simulados.
- Limpieza de datos/artefactos fake: `scripts/cleanup_fake_phase6_data.sh`.

Nota operativa:
- Ejecutar pytest por ruta de suite para evitar colisiones de import entre backups y servicios activos.

## Endpoints frontend recomendados (pendientes)

Los siguientes endpoints son recomendados para una UX completa de frontend, pero no forman parte del contrato activo actual:

- `GET /integration/offers/{offer_id}`
- `GET /integration/profiles/vector-status`
- Paginacion real de catalogo y recomendadas (`offset/cursor`)
- Endpoint de explicacion de score
