# 📦 Backup - Fase 1 (Base Inmutable)

## Propósito
Esta carpeta contiene una copia de seguridad de los archivos que forman la **Fase 1** del proyecto JobMatch.

⚠️ **IMPORTANTE**: Estos archivos son la referencia fija de esta fase y no deberían modificarse cuando empieces la Fase 2 o posteriores.

## Archivos incluidos

| Archivo | Qué representa |
|---------|----------------|
| `phase1_docker-compose.yml` | Infraestructura con el servicio `auth-service` añadido |
| `phase1_env.docker` | Variables de entorno de Docker para Fase 1 |
| `phase1_endpoints.md` | Documentación global de endpoints con Fase 1 incluida |
| `phase1_nginx.conf` | Proxy Nginx con rutas `/auth/*` |
| `phase1_auth-service/` | Código completo del servicio de autenticación |
| `phase1_README.md` | Documento resumen de la Fase 1 |
| `phase1_ENDPOINTS.md` | Endpoints específicos de la Fase 1 |
| `phase1_criterios-aceptacion.md` | Checklist de aceptación de la fase |

## Cómo usarlo

- Úsalo como referencia si algo se rompe en fases posteriores.
- Compárala con el código activo antes de tocar nada de Fase 1.
- No mezcles cambios de Fase 2 con este respaldo.

## Idea clave
Fase 1 ya está validada, así que este backup sirve para mantenerla igual que hicimos con Fase 0: una base cerrada, estable e inmune a cambios accidentales.
