# Explicacion de la Estructura - Fase 8

## Descripcion General
Fase 8 introduce un formulario de transicion profesional para que el usuario pueda declarar su objetivo de cambio de carrera aunque su CV refleje experiencia previa distinta.

---

### `services/profile-service/app/main.py` -> No eliminar (CRITICO)
**Proposito**: Publicar contrato API del formulario de objetivo profesional.

**Cambios de Fase 8**:
- `POST /profiles/cv` ahora acepta campos opcionales `desired_role` y `transition_summary`.
- Nuevo endpoint `PUT /profiles/career-goals` para guardar/actualizar formulario de transicion.
- `GET /profiles/me` devuelve los nuevos campos en el payload de perfil.

---

### `services/profile-service/app/services/profiles.py` -> No eliminar (CRITICO)
**Proposito**: Orquestar validacion y persistencia del formulario profesional.

**Cambios de Fase 8**:
- Validacion de consistencia de `desired_role` + `transition_summary`.
- Reglas para impedir formularios parciales.
- Metodo dedicado de negocio para actualizar objetivo profesional en un perfil existente.

---

### `services/profile-service/app/repositories/profiles.py` -> No eliminar (CRITICO)
**Proposito**: Persistencia SQL del objetivo de transicion.

**Cambios de Fase 8**:
- Soporte de columnas `desired_role` y `transition_summary`.
- Upsert de perfil ampliado con preservacion de datos previos.
- Nuevo update especifico para formulario profesional.
- Compatibilidad automatica de esquema al startup para BD existentes con volumen previo.

---

### `services/profile-service/app/models.py` y `services/profile-service/app/schemas.py` -> No eliminar (CRITICO)
**Proposito**: Contrato interno/API con nuevos campos de transicion profesional.

**Cambios de Fase 8**:
- Modelo de perfil extendido con `desired_role` y `transition_summary`.
- Nuevo schema `CareerGoalUpsertRequest`.
- Respuestas de perfil ampliadas para frontend.

---

### `services/profile-service/app/utils/cv_etl.py` -> No eliminar (CRITICO)
**Proposito**: Mantener JSON ETL coherente con el formulario profesional.

**Cambios de Fase 8**:
- Se agrega bloque `career_goal` al payload guardado en MinIO.

---

### `services/profile-service/tests/test_profiles.py` -> No eliminar (CRITICO)
**Proposito**: Cubrir la nueva funcionalidad sin regresiones.

**Cambios de Fase 8**:
- Tests de formulario inline en subida de CV.
- Tests de endpoint `PUT /profiles/career-goals`.
- Test de error para formulario parcial y para perfil inexistente.

---

### `init-db.sql` -> No eliminar (CRITICO)
**Proposito**: Esquema de datos de perfiles actualizado.

**Cambios de Fase 8**:
- Nuevas columnas en `profiles`: `desired_role`, `transition_summary`.
- `ALTER TABLE ... IF NOT EXISTS` para compatibilidad con entornos ya iniciados.

---

### `scripts/test_all_endpoints.sh` -> No eliminar (CRITICO)
**Proposito**: Validacion integral del flujo con formulario de transicion.

**Cambios de Fase 8**:
- Incluye llamada a `PUT /profiles/career-goals`.
- Verifica que `GET /profiles/me` refleje `desired_role` esperado.

---

### `endpoints.md` y `fases.md` -> No eliminar (CRITICO)
**Proposito**: Trazabilidad documental global de Fase 8.

**Cambios de Fase 8**:
- Nueva seccion de endpoints funcionales de transicion profesional.
- Registro oficial de entregables y cierre de fase.

---

### `Fase8/` -> No eliminar (CRITICO)
**Proposito**: Documentacion oficial y backup inmutable de la fase.

**Archivos esperados**:
- `README.md`
- `ENDPOINTS.md`
- `criterios-aceptacion.md`
- `explicacion-archivos.md`
- `_backup_phase8_base/`

---

## Hechos clave
- El perfil del usuario ya no depende solo de experiencia historica del CV.
- Se habilita un canal explicito para transiciones laborales (ejemplo: hosteleria -> arquitectura).
- La funcionalidad queda validada en tests unitarios y en script integral de endpoints.
- La fase queda documentada y respaldada de forma inmutable para trazabilidad.
