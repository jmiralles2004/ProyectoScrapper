# Backup - Fase 8 (Base Inmutable)

## Proposito
Esta carpeta contiene una copia de seguridad de los archivos que forman la Fase 8 del proyecto JobMatch.

IMPORTANTE: Estos archivos son referencia fija de la fase y no deben modificarse en fases posteriores.

## Archivos incluidos

| Archivo | Que representa |
|---------|----------------|
| `phase8_README.md` | Resumen de la Fase 8 |
| `phase8_endpoints_phase.md` | Endpoints especificos de la fase |
| `phase8_criterios-aceptacion.md` | Checklist de aceptacion |
| `phase8_explicacion-archivos.md` | Explicacion estructural de la fase |
| `phase8_init-db.sql` | Esquema de BD con campos de transicion profesional |
| `phase8_profile_main.py` | Entry point de profile-service con endpoint career goals |
| `phase8_profile_schemas.py` | Schemas API con formulario profesional |
| `phase8_profile_models.py` | Modelo interno de perfil ampliado |
| `phase8_profile_service.py` | Logica de negocio de validacion y guardado del formulario |
| `phase8_profile_repository.py` | Persistencia SQL de `desired_role` y `transition_summary` |
| `phase8_profile_cv_etl.py` | Payload ETL con bloque `career_goal` |
| `phase8_profile_tests.py` | Pruebas unitarias de flujo de formulario |
| `phase8_profile_README.md` | README actualizado del profile-service |
| `phase8_test_all_endpoints.sh` | Script integral con validacion de career goals |
| `phase8_endpoints_global.md` | Contrato global de endpoints actualizado |
| `phase8_fases.md` | Hoja maestra de fases con Fase 8 registrada |
| `phase8_explicacion-global.md` | Explicacion global actualizada |

## Como usarlo
- Usalo como referencia para recuperar el estado cerrado de la fase.
- Comparalo con codigo activo antes de introducir cambios futuros.
- No mezclar este respaldo con modificaciones de otras fases.

## Idea clave
Fase 8 queda cerrada y trazable con su backup inmutable.
