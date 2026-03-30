# 🔌 Endpoints de JobMatch

## Descripción General
Este documento lista los endpoints disponibles en el proyecto, empezando por la infraestructura base y la autenticación de la Fase 1.

---

## 🏗️ FASE 0 - Infraestructura Base

**Estado**: ✅ Activo  
**Propósito**: Validar que la infraestructura funciona

| Método | Ruta | Servicio | Descripción |
|--------|------|---------|------------|
| `GET` | `/health` | Nginx | Verifica que Nginx está vivo (Docker healthcheck) |

**Ejemplo**:
```bash
curl http://localhost/health
```

**Respuesta** (HTTP 200):
```json
{"status":"ok","service":"nginx-proxy"}
```

---

## 🔐 FASE 1 - Auth Service

**Estado**: ✅ Activo  
**Propósito**: Registro, login y validación JWT

| Método | Ruta | Servicio | Descripción |
|--------|------|---------|------------|
| `GET` | `/health` | Auth Service | Comprueba que el servicio está operativo |
| `GET` | `/auth/health` | Auth Service | Alias público del healthcheck a través de Nginx |
| `POST` | `/auth/register` | Auth Service | Registra un usuario nuevo |
| `POST` | `/auth/login` | Auth Service | Inicia sesión y devuelve un JWT |
| `GET` | `/auth/me` | Auth Service | Devuelve el usuario autenticado |

**Ejemplo de registro**:
```bash
curl -X POST http://localhost/auth/register \
	-H "Content-Type: application/json" \
	-d '{"email":"user@example.com","password":"secret123"}'
```

**Ejemplo de login**:
```bash
curl -X POST http://localhost/auth/login \
	-H "Content-Type: application/json" \
	-d '{"email":"user@example.com","password":"secret123"}'
```

**Respuesta de login**:
```json
{"access_token":"<jwt>","token_type":"bearer"}
```

**Notas**:
- Los endpoints se exponen a través de Nginx en `/auth/*`
- `Authorization: Bearer <token>` es obligatorio para `/auth/me`
- El usuario se guarda en PostgreSQL en la tabla `users`