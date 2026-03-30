# Explicación de la Estructura - Fase 6

## 📋 Descripción General
Fase 6 añade el **servicio de integración** al proyecto JobMatch. Esta fase conecta un proveedor externo de ofertas/vectores con la base vectorial (Qdrant) y expone recomendaciones personalizadas por perfil de cliente.

---

### `services/integration-service/` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Contiene la API y la lógica de Fase 6 para integración y recomendaciones.

**Archivos**:
- `Dockerfile`: Construye el contenedor del servicio
- `requirements.txt`: Dependencias del servicio
- `app/main.py`: Endpoints `/integration/*` y healthchecks
- `app/services/integration.py`: Orquestación de ingesta y ranking
- `app/vectorstore/qdrant_store.py`: Operaciones con Qdrant
- `tests/test_integration.py`: Pruebas unitarias del flujo principal

---

### `docker-compose.yml` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Integra `integration-service` con Qdrant y Nginx.

**Puntos clave de Fase 6**:
- Nuevo servicio: `integration-service`
- Dependencia de `qdrant`
- Variables de integración y colecciones vectoriales por entorno
- Healthcheck activo para que Nginx espere al servicio

---

### `nginx-proxy/nginx.conf` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Publica las rutas de integración al exterior.

**Rutas de Fase 6**:
- `/integration/health`
- `/integration/offers/import`
- `/integration/profiles/import-vector`
- `/integration/offers/catalog`
- `/integration/offers/recommended`

---

### `.env` y `.env.docker` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Definen configuración del servicio de integración.

**Variables añadidas en Fase 6**:
- `INTEGRATION_SERVICE_PORT`
- `INTEGRATION_VECTOR_SIZE`
- `QDRANT_COLLECTION_PROFILES`
- `QDRANT_COLLECTION_OFFERS`
- `INTEGRATION_INGEST_API_KEY`

---

### `Fase6/` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Contiene documentación oficial y respaldo inmutable de la fase.

**Archivos esperados**:
- `README.md`
- `ENDPOINTS.md`
- `criterios-aceptacion.md`
- `explicacion-archivos.md`
- `_backup_phase6_base/`

---

## ✅ Hechos clave
- La plataforma no calcula embeddings internamente: los recibe de fuente externa.
- Qdrant actúa como base vectorial para catálogo y recomendación.
- El endpoint de recomendación usa JWT para devolver ofertas adaptadas al perfil del cliente.

---

## Validacion obligatoria y evidencia operativa

### Suites de pruebas verificadas
- Activas: `services/auth-service/tests`, `services/profile-service/tests`, `services/integration-service/tests`.
- Backup de fase: `Fase1/_backup_phase1_base/phase1_auth-service/tests`, `Fase2/_backup_phase2_base/phase2_profile-service/tests`, `Fase6/_backup_phase6_base/phase6_integration-service/tests`.

### Que persiste cada tipo de prueba
- Auth unit tests: usuarios en repositorio fake en memoria.
- Profile unit tests: perfiles y payload ETL en memoria (repo/storage fake).
- Integration unit tests: ofertas y vectores en memoria (vector store fake).
- Smoke test Fase 6: datos simulados reales en Qdrant + resumen en `/tmp/phase6-smoke-summary.json`.

### Recomendacion de ejecucion
- Evitar `pytest -q` en raiz cuando conviven backups y servicios activos, porque hay colisiones de import por modulos `app` con el mismo nombre.
- Ejecutar por ruta de suite para garantizar aislamiento y resultados consistentes.
