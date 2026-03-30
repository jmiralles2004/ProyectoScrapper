# 📦 Backup - Fase 2 (Base Inmutable)

## Propósito
Esta carpeta contiene una copia de seguridad de los archivos que forman la **Fase 2** del proyecto JobMatch.

⚠️ **IMPORTANTE**: Estos archivos son la referencia fija de esta fase y no deberían modificarse cuando empieces la Fase 3 o posteriores.

## Archivos incluidos

| Archivo | Qué representa |
|---------|----------------|
| `phase2_docker-compose.yml` | Infraestructura con `profile-service` integrado |
| `phase2_env.docker` | Variables de entorno Docker para Fase 2 |
| `phase2_endpoints_global.md` | Documentación global de endpoints con Fase 2 incluida |
| `phase2_nginx.conf` | Proxy Nginx con rutas `/profiles/*` |
| `phase2_init-db.sql` | Esquema SQL incluyendo tabla `profiles` |
| `phase2_profile-service/` | Código completo del servicio de perfiles (incluye OCR + ETL base) |
| `phase2_explicacion-archivos.md` | Explicación estructural de Fase 2 |
| `phase2_README.md` | Resumen de la Fase 2 |
| `phase2_endpoints_phase.md` | Endpoints específicos de la Fase 2 |
| `phase2_criterios-aceptacion.md` | Checklist de aceptación de la fase |

## Cómo usarlo

- Úsalo como referencia si algo se rompe en fases posteriores.
- Compáralo con el código activo antes de tocar nada de Fase 2.
- No mezcles cambios de Fase 3 con este respaldo.

## Idea clave
Fase 2 queda validada y congelada con el mismo enfoque de Fase 0 y Fase 1: una base cerrada, estable e inmune a cambios accidentales.
