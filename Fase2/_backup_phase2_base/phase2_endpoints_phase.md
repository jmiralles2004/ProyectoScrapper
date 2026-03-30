# Endpoints - Fase 2

## Fase 2 - Profile Service

| Método | Ruta | Servicio | Descripción |
|--------|------|---------|------------|
| `GET` | `/profiles/health` | Profile Service | Comprueba que el servicio está operativo |
| `POST` | `/profiles/cv` | Profile Service | Sube un CV en PDF, extrae texto (con OCR si hace falta) y guarda perfil en formato ETL |
| `GET` | `/profiles/me` | Profile Service | Devuelve el perfil del usuario autenticado |

## Uso
Los endpoints de perfiles se consumen a través de Nginx usando la ruta `/profiles/*`.
La subida en `/profiles/cv` genera un JSON ETL en MinIO con bloques `raw`, `normalized` y `quality`.
