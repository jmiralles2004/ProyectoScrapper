# Explicacion de la Estructura - Fase 8

## Descripcion General
Fase 8 incorpora un formulario para que el usuario defina su objetivo de cambio profesional y no dependa solo del CV historico.

### `services/profile-service/app/main.py` -> No eliminar (CRITICO)
- Expone `PUT /profiles/career-goals`.
- Amplia `POST /profiles/cv` para aceptar `desired_role` y `transition_summary`.

### `services/profile-service/app/services/profiles.py` -> No eliminar (CRITICO)
- Añade validaciones de consistencia para formulario profesional.
- Implementa guardado/actualizacion de objetivo profesional.

### `services/profile-service/app/repositories/profiles.py` -> No eliminar (CRITICO)
- Amplia lectura y upsert de perfiles con `desired_role` y `transition_summary`.
- Añade update especifico para formulario profesional.
- Ejecuta compatibilidad de esquema al arranque (`ALTER TABLE ... IF NOT EXISTS`) para entornos con volumenes de BD antiguos.

### `services/profile-service/app/models.py` y `services/profile-service/app/schemas.py` -> No eliminar (CRITICO)
- Actualiza contrato interno/API con campos de objetivo profesional.

### `services/profile-service/app/utils/cv_etl.py` -> No eliminar (CRITICO)
- Incluye bloque `career_goal` en payload ETL de MinIO.

### `services/profile-service/tests/test_profiles.py` -> No eliminar (CRITICO)
- Cubre flujo de formulario inline y endpoint dedicado.

### `init-db.sql` -> No eliminar (CRITICO)
- Agrega columnas en `profiles` para objetivo profesional.
- Incluye `ALTER TABLE ... IF NOT EXISTS` para compatibilidad.

### `scripts/test_all_endpoints.sh` -> No eliminar (CRITICO)
- Valida `PUT /profiles/career-goals` y persistencia visible en `/profiles/me`.

### `Fase8/_backup_phase8_base/` -> No eliminar (CRITICO)
- Guarda snapshot inmutable de artefactos de la fase.

## Hechos clave
- El usuario puede declarar una transicion de carrera explicita (ejemplo: hosteleria -> arquitectura).
- El formulario queda persistido en BD y trazado en el JSON ETL.
- La fase queda cubierta en pruebas y documentacion global.
