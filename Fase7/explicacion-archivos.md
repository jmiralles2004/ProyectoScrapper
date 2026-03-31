# Explicacion de la Estructura - Fase 7

## Descripcion General
Fase 7 introduce una capa de documentacion OpenAPI/Swagger accesible por prefijos de gateway para los tres microservicios activos.

### `docker-compose.yml` -> No eliminar (CRITICO)
- Integra el contenedor `swagger-ui` para portal documental unificado.

### `nginx-proxy/nginx.conf` -> No eliminar (CRITICO)
- Publica `GET /swagger/` y enruta al contenedor `swagger-ui`.

### `scripts/test_all_endpoints.sh` -> No eliminar (CRITICO)
- Ejecuta validacion integral end-to-end de endpoints de infraestructura, negocio y documentacion.

### `services/auth-service/app/main.py` -> No eliminar (CRITICO)
- Expone `GET /auth/docs` y `GET /auth/openapi.json`.

### `services/profile-service/app/main.py` -> No eliminar (CRITICO)
- Expone `GET /profiles/docs` y `GET /profiles/openapi.json`.

### `services/integration-service/app/main.py` -> No eliminar (CRITICO)
- Expone `GET /integration/docs` y `GET /integration/openapi.json`.

### `endpoints.md` -> No eliminar (CRITICO)
- Documenta todos los endpoints de negocio y de documentacion.

### `fases.md` -> No eliminar (CRITICO)
- Declara oficialmente Fase 7 en la hoja maestra del proyecto.

### `_backup_phase7_base/` -> No eliminar (CRITICO)
- Guarda la referencia inmutable de la fase para trazabilidad y recuperacion.

## Hechos clave
- No hay logica de negocio nueva en esta fase.
- Se habilita contrato API vivo para frontend, QA e integraciones.
- Existe una UI unificada en `/swagger/` para navegar los 3 contratos OpenAPI.
- Existe script unico para validar toda la superficie de endpoints en una sola ejecucion.
- Se recomienda securizar rutas docs/openapi en produccion.
