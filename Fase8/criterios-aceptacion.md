# Criterios de aceptacion - Fase 8

- `PUT /profiles/career-goals` responde correctamente con JWT valido.
- `PUT /profiles/career-goals` devuelve 404 si el usuario no ha subido CV previamente.
- `POST /profiles/cv` acepta `desired_role` y `transition_summary` opcionales en multipart/form-data.
- `POST /profiles/cv` devuelve 422 cuando llega formulario parcial (solo uno de los dos campos).
- `GET /profiles/me` refleja los campos `desired_role` y `transition_summary` guardados.
- `init-db.sql` incluye columnas `profiles.desired_role` y `profiles.transition_summary` con compatibilidad para entornos existentes.
- El JSON ETL de MinIO incluye bloque `career_goal`.
- El test integral `scripts/test_all_endpoints.sh` valida el flujo del formulario de transicion profesional.
- Se mantiene compatibilidad de endpoints ya existentes de Auth, Profile e Integration.
- `endpoints.md`, `fases.md` y `explicacion-archivos.md` quedan actualizados con Fase 8.
- Existe backup inmutable en `Fase8/_backup_phase8_base/`.
