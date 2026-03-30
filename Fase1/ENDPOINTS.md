# Endpoints - Fase 1

## Fase 1 - Auth Service

| Método | Ruta | Servicio | Descripción |
|--------|------|---------|------------|
| `GET` | `/health` | Auth Service | Comprueba que el servicio está operativo |
| `GET` | `/auth/health` | Auth Service | Alias expuesto por Nginx para la misma comprobación |
| `POST` | `/auth/register` | Auth Service | Registra un usuario nuevo |
| `POST` | `/auth/login` | Auth Service | Inicia sesión y devuelve un JWT |
| `GET` | `/auth/me` | Auth Service | Devuelve el usuario autenticado |

## Uso
Todos los endpoints de autenticación se consumen a través de Nginx usando la ruta `/auth/*`.
