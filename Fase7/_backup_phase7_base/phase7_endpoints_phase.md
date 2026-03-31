# Endpoints - Fase 7

## Fase 7 - Documentacion OpenAPI/Swagger por Gateway

| Metodo | Ruta | Servicio | Descripcion |
|--------|------|---------|-------------|
| `GET` | `/auth/docs` | Auth Service | Swagger UI de autenticacion |
| `GET` | `/auth/openapi.json` | Auth Service | OpenAPI JSON de autenticacion |
| `GET` | `/profiles/docs` | Profile Service | Swagger UI de perfiles |
| `GET` | `/profiles/openapi.json` | Profile Service | OpenAPI JSON de perfiles |
| `GET` | `/integration/docs` | Integration Service | Swagger UI de integracion |
| `GET` | `/integration/openapi.json` | Integration Service | OpenAPI JSON de integracion |

## Uso
- Estas rutas se consumen a traves de Nginx usando los prefijos funcionales.
- No reemplazan endpoints de negocio; son endpoints de documentacion tecnica.

## Nota de seguridad
- En produccion, proteger estas rutas con auth o red interna.
