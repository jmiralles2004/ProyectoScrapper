# Backup - Fase 6 (Base Inmutable)

## Proposito
Esta carpeta contiene una copia de seguridad de los archivos que forman la **Fase 6** del proyecto JobMatch.

IMPORTANTE: Estos archivos son la referencia fija de esta fase y no deben modificarse en fases posteriores.

## Archivos incluidos

| Archivo | Que representa |
|---------|----------------|
| `phase6_docker-compose.yml` | Infraestructura con `integration-service` integrado |
| `phase6_env.docker` | Variables de entorno Docker para Fase 6 |
| `phase6_endpoints.md` | Documentacion global de endpoints con Fase 6 incluida |
| `phase6_nginx.conf` | Proxy Nginx con rutas `/integration/*` |
| `phase6_explicacion-archivos.md` | Explicacion estructural de la fase |
| `phase6_integration-service/` | Codigo completo del servicio de integracion |
| `phase6_INTEGRACION_DATOS_EXTERNOS.md` | Guia exacta de donde conectar ofertas y vectores externos |
| `phase6_scripts/` | Scripts de smoke test y limpieza de datos simulados |
| `phase6_README.md` | Resumen de la Fase 6 |
| `phase6_ENDPOINTS.md` | Endpoints especificos de la Fase 6 |
| `phase6_criterios-aceptacion.md` | Checklist de aceptacion de la fase |

## Como usarlo

- Usalo como referencia si algo se rompe en fases posteriores.
- Comparalo con el codigo activo antes de tocar Fase 6.
- No mezcles cambios de otras fases con este respaldo.

## Idea clave
Fase 6 queda validada y congelada como base cerrada e inmutable.
