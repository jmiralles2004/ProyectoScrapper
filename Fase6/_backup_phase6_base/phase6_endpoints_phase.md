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
