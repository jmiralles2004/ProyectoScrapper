# 🔌 Endpoints de JobMatch

## Descripción General
Este documento lista los endpoints disponibles en el proyecto, incluyendo endpoints funcionales y endpoints de documentacion tecnica por fase.

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

---

## 🔗 FASE 6 - Integration Service

**Estado**: ✅ Activo  
**Propósito**: Importar ofertas y vectores externos y devolver recomendaciones personalizadas por perfil

| Método | Ruta | Servicio | Descripción |
|--------|------|---------|------------|
| `GET` | `/integration/health` | Integration Service | Verifica que el servicio está operativo |
| `POST` | `/integration/offers/import` | Integration Service | Importa lote de ofertas con sus vectores desde proveedor externo |
| `POST` | `/integration/profiles/import-vector` | Integration Service | Importa vector de perfil de un usuario |
| `GET` | `/integration/offers/catalog` | Integration Service | Lista catálogo de ofertas almacenadas en base vectorial |
| `GET` | `/integration/offers/recommended` | Integration Service | Devuelve ofertas recomendadas para el usuario autenticado |

**Ejemplo de importación de ofertas**:
```bash
curl -X POST http://localhost/integration/offers/import \
	-H "x-internal-api-key: <internal-key>" \
	-H "Content-Type: application/json" \
	-d '{
		"offers": [
			{
				"offer_id": "offer-1",
				"title": "Backend Developer",
				"company": "Acme",
				"description": "Python FastAPI role",
				"vector": [0.1, 0.2, 0.3, 0.4]
			}
		]
	}'
```

**Ejemplo de recomendación**:
```bash
curl "http://localhost/integration/offers/recommended?limit=10" \
	-H "Authorization: Bearer <token>"
```

**Notas**:
- Los endpoints de ingesta usan `x-internal-api-key` cuando está configurado
- Los vectores se guardan en Qdrant en `profile_vectors` y `offer_vectors`
- `/integration/offers/recommended` calcula ranking por similitud vectorial en tiempo real
- Los ejemplos de Fase 6 usan datos simulados/falsos y son solo para testear el comportamiento tecnico

---

## 📘 FASE 7 - Documentación OpenAPI/Swagger por Gateway

**Estado**: ✅ Activo  
**Propósito**: Exponer la documentación viva de cada microservicio a través de Nginx con prefijos estables.

| Método | Ruta | Servicio | Descripción |
|--------|------|---------|------------|
| `GET` | `/auth/docs` | Auth Service | Swagger UI del servicio de autenticación |
| `GET` | `/auth/openapi.json` | Auth Service | Contrato OpenAPI JSON del servicio de autenticación |
| `GET` | `/profiles/docs` | Profile Service | Swagger UI del servicio de perfiles |
| `GET` | `/profiles/openapi.json` | Profile Service | Contrato OpenAPI JSON del servicio de perfiles |
| `GET` | `/integration/docs` | Integration Service | Swagger UI del servicio de integración |
| `GET` | `/integration/openapi.json` | Integration Service | Contrato OpenAPI JSON del servicio de integración |
| `GET` | `/swagger/` | Swagger UI Container | Portal unificado con selector de contratos OpenAPI del backend |

**Ejemplos**:
```bash
curl http://localhost/auth/docs
curl http://localhost/profiles/openapi.json
curl http://localhost/integration/docs
curl http://localhost/swagger/
```

**Notas**:
- Esta fase no añade endpoints de negocio nuevos, solo endpoints de documentación técnica.
- Los contratos OpenAPI son útiles para frontend, QA y clientes API.
- `/swagger/` centraliza en una sola UI los contratos de Auth, Profile e Integration.
- En producción se recomienda proteger estas rutas (auth, allowlist o red interna).

---

## Estado de validacion y persistencia de tests (Fase 6)

- Suites activas verificadas: `services/auth-service/tests`, `services/profile-service/tests`, `services/integration-service/tests`.
- Suites de backup verificadas: `Fase1/_backup_phase1_base/phase1_auth-service/tests`, `Fase2/_backup_phase2_base/phase2_profile-service/tests`, `Fase6/_backup_phase6_base/phase6_integration-service/tests`.
- `Auth` unit tests: persisten en repositorio fake en memoria (sin PostgreSQL real).
- `Profile` unit tests: persisten en repositorio fake + storage fake en memoria (sin PostgreSQL/MinIO reales).
- `Integration` unit tests: persisten en vector store fake en memoria (sin Qdrant real).
- `scripts/phase6_smoke_test.sh`: persiste datos simulados reales en Qdrant y guarda resumen tecnico en `/tmp/phase6-smoke-summary.json`.
- Limpieza total de artefactos fake: `scripts/cleanup_fake_phase6_data.sh`.

Nota operativa:
- Ejecutar `pytest -q` en la raiz puede provocar colisiones de import entre servicios activos y backups (modulos `app` duplicados). La ejecucion fiable se hace por suite/ruta.

---

## Endpoints recomendados para frontend (pendientes, no implementados)

Estos endpoints son recomendados para evolucion del frontend. No forman parte del contrato activo actual:

- `GET /integration/offers/{offer_id}`: detalle completo de oferta por id externo.
- `GET /integration/profiles/vector-status`: estado del vector de perfil del usuario autenticado.
- Paginacion real para catalogo y recomendadas (`offset/cursor`) ademas de `limit`.
- Endpoint de explicacion de score para trazabilidad UX (por ejemplo, factores de similitud principales).