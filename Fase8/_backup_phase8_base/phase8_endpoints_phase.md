# Endpoints - Fase 8

## Fase 8 - Formulario de Transicion Profesional

| Metodo | Ruta | Servicio | Descripcion |
|--------|------|---------|-------------|
| `POST` | `/profiles/cv` | Profile Service | Sube CV y acepta opcionalmente `desired_role` y `transition_summary` en multipart/form-data |
| `PUT` | `/profiles/career-goals` | Profile Service | Guarda/actualiza el formulario de objetivo profesional del usuario autenticado |
| `GET` | `/profiles/me` | Profile Service | Devuelve perfil con `desired_role` y `transition_summary` si existen |

## Uso
- Todas las rutas de perfil se consumen por Nginx en `/profiles/*`.
- `PUT /profiles/career-goals` requiere JWT Bearer y perfil existente (CV ya subido).
- Si se envia formulario parcial (solo un campo) en `POST /profiles/cv`, se devuelve HTTP 422.

## Ejemplo
```bash
curl -X PUT http://localhost/profiles/career-goals \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "desired_role": "Arquitecto",
    "transition_summary": "Quiero reconvertirme al sector de arquitectura tras anos en hosteleria"
  }'
```
