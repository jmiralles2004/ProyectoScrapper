# Explicación de la Estructura - Fase 2

## 📋 Descripción General
Fase 2 añade el **servicio de perfiles** al proyecto JobMatch. Esta fase permite subir CVs en PDF, extraer su texto (incluyendo OCR para PDFs escaneados) y guardar tanto metadatos como contenido para usarlos en fases posteriores.

---

### `services/profile-service/` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Contiene la API y la lógica de Fase 2 para perfil de candidato.

**Archivos**:
- `Dockerfile`: Construye el contenedor del servicio
- `requirements.txt`: Dependencias del servicio
- `app/main.py`: Endpoints `/profiles/*` y healthchecks
- `app/repositories/profiles.py`: Persistencia en PostgreSQL
- `app/storage/minio_storage.py`: Guardado de JSON en MinIO
- `app/utils/pdf.py`: Extracción híbrida (texto embebido + OCR con Tesseract)
- `app/utils/cv_etl.py`: Normalización y ETL base del CV (secciones, entidades, quality)
- `tests/test_profiles.py`: Pruebas unitarias del flujo principal

---

### `docker-compose.yml` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Integra `profile-service` con PostgreSQL, MinIO y Nginx.

**Puntos clave de Fase 2**:
- Nuevo servicio: `profile-service` (puerto interno 8000)
- Variables de MinIO y JWT inyectadas por entorno
- Healthcheck activo para que Nginx espere al servicio

---

### `nginx-proxy/nginx.conf` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Publica las rutas de perfiles al exterior.

**Rutas de Fase 2**:
- `/profiles/health`
- `/profiles/cv`
- `/profiles/me`

---

### `init-db.sql` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Crea la nueva tabla `profiles`.

**¿Qué guarda `profiles`?**
- Relación 1:1 con `users` (`user_id` único)
- Nombre de archivo original (`cv_filename`)
- Texto extraído (`cv_text`)
- Referencia al JSON en MinIO (`cv_object_key`)

---

### `Fase2/` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Contiene la documentación oficial de la fase y su respaldo inmutable.

**Archivos**:
- `README.md`
- `ENDPOINTS.md`
- `criterios-aceptacion.md`
- `explicacion-archivos.md`
- `_backup_phase2_base/`

---

## ✅ Hechos clave
- Se mantiene JWT como mecanismo de autenticación.
- El CV se sube en PDF y se procesa en backend (con OCR cuando viene escaneado).
- Los datos se guardan en PostgreSQL y MinIO en formato ETL (`raw`, `normalized`, `quality`).
- Fase 2 queda preparada para Fase 3 (embeddings).
