# Fase 2 - Profile Service + MinIO

## Objetivo
Implementar la gestión de perfiles del candidato con subida de CV en PDF, extracción de texto (incluyendo OCR para escaneados) y almacenamiento en MinIO.

## Qué incluye
- Servicio FastAPI `profile-service`
- Endpoint para subida de CV (`POST /profiles/cv`)
- Endpoint para consultar perfil actual (`GET /profiles/me`)
- Healthchecks (`/health` y `/profiles/health`)
- Persistencia en PostgreSQL (tabla `profiles`)
- Guardado de JSON en MinIO (bucket `profiles`)
- OCR automático cuando el PDF no trae texto embebido
- ETL base del CV (raw + normalizado + secciones + entidades + quality score)
- Protección con JWT Bearer

## Componentes
- `services/profile-service/` - Código y tests del servicio de perfiles
- `docker-compose.yml` - Servicio `profile-service` integrado
- `nginx-proxy/nginx.conf` - Proxy de rutas `/profiles/*`
- `init-db.sql` - Nueva tabla `profiles`
- `endpoints.md` - Endpoints globales de Fase 2 documentados
- `explicacion-archivos.md` - Explicación estructural de la fase
- `_backup_phase2_base/` - Copia inmune de referencia

## Criterio de fase completada
La fase se considera lista cuando el servicio arranca con Docker, permite subir CVs PDF con JWT (incluyendo escaneados vía OCR), guarda datos en PostgreSQL/MinIO, genera JSON ETL estructurado y responde correctamente en `/profiles/health` y `/profiles/me`.
