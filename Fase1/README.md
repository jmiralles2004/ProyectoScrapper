# Fase 1 - Auth Service

## Objetivo
Implementar autenticación básica para JobMatch con registro, login y acceso a datos del usuario autenticado mediante JWT.

## Qué incluye
- Servicio FastAPI de autenticación
- Registro de usuarios en PostgreSQL
- Login con token JWT
- Endpoint protegido `/auth/me`
- Healthcheck interno `/health` y alias público `/auth/health`
- Integración con Nginx en `/auth/*`

## Componentes
- `services/auth-service/` - Código del servicio
- `docker-compose.yml` - Servicio añadido a la infraestructura
- `nginx-proxy/nginx.conf` - Proxy de rutas `/auth/*`
- `endpoints.md` - Endpoints de Fase 1 documentados

## Criterio de fase completada
La fase se considera lista cuando el servicio arranca con Docker, responde a `/health`, permite registrar usuarios, hacer login y consultar `/auth/me` con JWT.
