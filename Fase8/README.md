# Fase 8 - Formulario de Transicion Profesional

## Objetivo
Permitir que el usuario declare un objetivo profesional de cambio de carrera para que su perfil no dependa solo del historial del CV.

## Que incluye
- Endpoint dedicado `PUT /profiles/career-goals` para guardar formulario de transicion profesional.
- Extension de `POST /profiles/cv` para aceptar opcionalmente `desired_role` y `transition_summary`.
- `GET /profiles/me` ahora devuelve `desired_role` y `transition_summary` cuando existen.
- Persistencia en PostgreSQL de `profiles.desired_role` y `profiles.transition_summary`.
- Inclusion de `career_goal` en el JSON ETL guardado en MinIO.
- Tests unitarios actualizados en `services/profile-service/tests/test_profiles.py`.
- Validacion integral del endpoint nuevo en `scripts/test_all_endpoints.sh`.

## Componentes
- `services/profile-service/` - Logica, esquemas y tests del formulario de transicion.
- `init-db.sql` - Nuevas columnas de perfil para objetivo profesional.
- `scripts/test_all_endpoints.sh` - Flujo integral con validacion de `PUT /profiles/career-goals`.
- `endpoints.md` - Contrato global actualizado con Fase 8.
- `explicacion-archivos.md` - Explicacion estructural global de la fase.
- `_backup_phase8_base/` - Copia inmune de referencia.

## Criterio de fase completada
La fase se considera lista cuando un usuario autenticado puede guardar su objetivo profesional (aunque su experiencia previa sea distinta), recuperar ese objetivo en `/profiles/me`, y el flujo queda documentado y validado.

## Verificacion rapida
```bash
curl -X PUT http://localhost/profiles/career-goals \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "desired_role": "Arquitecto",
    "transition_summary": "He trabajado en hosteleria y quiero orientar mi carrera a arquitectura"
  }'

curl -H "Authorization: Bearer <token>" http://localhost/profiles/me
```

## Verificacion integral automatizada
```bash
scripts/test_all_endpoints.sh
```
