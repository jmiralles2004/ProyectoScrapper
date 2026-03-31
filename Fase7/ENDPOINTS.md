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
| `GET` | `/swagger/` | Swagger UI Container | Portal unificado con selector de contratos OpenAPI |

## Uso
- Estas rutas se consumen a traves de Nginx usando los prefijos funcionales.
- `/swagger/` concentra en una sola interfaz los contratos de todos los microservicios.
- No reemplazan endpoints de negocio; son endpoints de documentacion tecnica.
- Validacion integral recomendada: `scripts/test_all_endpoints.sh`.

## Nota de seguridad
- En produccion, proteger estas rutas con auth o red interna.
