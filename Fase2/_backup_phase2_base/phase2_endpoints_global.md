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

---

## 👤 FASE 2 - Profile Service + MinIO

**Estado**: ✅ Activo  
**Propósito**: Subida de CV (PDF), extracción de texto y guardado en MinIO

| Método | Ruta | Servicio | Descripción |
|--------|------|---------|------------|
| `GET` | `/profiles/health` | Profile Service | Verifica que el servicio de perfiles está operativo |
| `POST` | `/profiles/cv` | Profile Service | Sube un CV en PDF, extrae texto y guarda JSON en MinIO |
| `GET` | `/profiles/me` | Profile Service | Devuelve el perfil/CV del usuario autenticado |

**Ejemplo de subida de CV**:
```bash
curl -X POST http://localhost/profiles/cv \
		-H "Authorization: Bearer <token>" \
		-F "file=@./mi_cv.pdf"
```

**Respuesta de subida**:
```json
{
	"id": "<profile-id>",
	"user_id": "<user-id>",
	"cv_filename": "mi_cv.pdf",
	"cv_object_key": "profiles/<user-id>/cv_20260330....json",
	"storage_bucket": "profiles",
	"extracted_text_length": 12345,
	"created_at": "2026-03-30T12:00:00Z",
	"updated_at": "2026-03-30T12:00:00Z"
}
```

**Notas**:
- `/profiles/cv` y `/profiles/me` requieren JWT válido
- El texto extraído del PDF se guarda en PostgreSQL (`profiles.cv_text`)
- Si el PDF llega escaneado, se aplica OCR automáticamente antes de guardar
- El JSON completo del perfil se guarda en MinIO (bucket `profiles`) con estructura ETL (`raw`, `normalized`, `quality`)