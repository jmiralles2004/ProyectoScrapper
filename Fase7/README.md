# Fase 7 - Documentacion OpenAPI/Swagger por Gateway

## Objetivo
Exponer de forma estable la documentacion tecnica de los microservicios (Auth, Profile e Integration) a traves del gateway Nginx para facilitar consumo por frontend, QA e integraciones.

## Que incluye
- Contenedor dedicado `swagger-ui` para documentacion unificada en `GET /swagger/`
- Rutas Swagger por prefijo:
  - `GET /auth/docs`
  - `GET /profiles/docs`
  - `GET /integration/docs`
- Rutas OpenAPI JSON por prefijo:
  - `GET /auth/openapi.json`
  - `GET /profiles/openapi.json`
  - `GET /integration/openapi.json`
- Actualizacion de documentacion global (`fases.md`, `endpoints.md`, `explicacion-archivos.md`).
- Carpeta de respaldo inmutable en `_backup_phase7_base/`.

## Componentes
- `docker-compose.yml` - Servicio `swagger-ui` integrado en la red del proyecto.
- `nginx-proxy/nginx.conf` - Publicacion de `swagger-ui` en `/swagger/`.
- `services/auth-service/app/main.py` - Swagger/OpenAPI por prefijo de auth.
- `services/profile-service/app/main.py` - Swagger/OpenAPI por prefijo de profiles.
- `services/integration-service/app/main.py` - Swagger/OpenAPI por prefijo de integration.
- `endpoints.md` - Contrato global actualizado con rutas de documentacion de Fase 7.
- `fases.md` - Hoja maestra actualizada con Fase 7 y su registro operativo.
- `explicacion-archivos.md` - Explicacion global actualizada para Fase 7.

## Criterio de fase completada
La fase se considera lista cuando existe portal unificado en `/swagger/`, la documentacion Swagger/OpenAPI JSON de los 3 microservicios responde por el gateway y la documentacion de fase/global queda cerrada y respaldada.

## Verificacion rapida
```bash
curl -I http://localhost/auth/docs
curl http://localhost/auth/openapi.json
curl -I http://localhost/profiles/docs
curl http://localhost/profiles/openapi.json
curl -I http://localhost/integration/docs
curl http://localhost/integration/openapi.json
curl -I http://localhost/swagger/
```

## Nota de seguridad
En entornos de produccion, estas rutas deben protegerse con autenticacion, allowlist de red o ambos mecanismos.
