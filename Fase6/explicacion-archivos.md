# Explicacion de la Estructura - Fase 6

## Descripcion General
Fase 6 implementa la integracion final del proyecto: ingesta de ofertas/vectores externos y recomendacion personalizada por perfil del cliente.

---

### `services/integration-service/` -> No eliminar (CRITICO)
**Proposito**: API y logica de negocio de integracion final.

**Archivos**:
- `Dockerfile`: Imagen del servicio
- `requirements.txt`: Dependencias
- `app/main.py`: Endpoints `/integration/*` y healthchecks
- `app/services/integration.py`: Reglas de ingesta y recomendaciones
- `app/vectorstore/qdrant_store.py`: Acceso a base vectorial Qdrant
- `tests/test_integration.py`: Tests unitarios

---

### `docker-compose.yml` -> No eliminar (CRITICO)
**Proposito**: Integra `integration-service` con Qdrant y Nginx.

**Puntos clave de Fase 6**:
- Nuevo servicio: `integration-service`
- Dependencia de `qdrant`
- Variables de colecciones y seguridad por entorno
- Healthcheck activo

---

### `nginx-proxy/nginx.conf` -> No eliminar (CRITICO)
**Proposito**: Publica rutas del servicio de integracion.

**Rutas de Fase 6**:
- `/integration/health`
- `/integration/offers/import`
- `/integration/profiles/import-vector`
- `/integration/offers/catalog`
- `/integration/offers/recommended`

---

### `.env` y `.env.docker` -> No eliminar (CRITICO)
**Proposito**: Configuracion del servicio de integracion.

**Variables de Fase 6**:
- `INTEGRATION_SERVICE_PORT`
- `INTEGRATION_VECTOR_SIZE`
- `QDRANT_COLLECTION_PROFILES`
- `QDRANT_COLLECTION_OFFERS`
- `INTEGRATION_INGEST_API_KEY`

---

### `Fase6/` -> No eliminar (CRITICO)
**Proposito**: Documentacion oficial de la fase y respaldo inmutable.

**Archivos**:
- `README.md`
- `ENDPOINTS.md`
- `criterios-aceptacion.md`
- `explicacion-archivos.md`
- `INTEGRACION_DATOS_EXTERNOS.md`
- `_backup_phase6_base/`

---

### `scripts/` -> No eliminar (CRITICO)
**Proposito**: Automatizar validacion tecnica y limpieza de datos simulados.

**Scripts de Fase 6**:
- `phase6_smoke_test.sh`: Ejecuta smoke test end-to-end con datos falsos/simulados
- `cleanup_fake_phase6_data.sh`: Elimina artefactos fake (contenedores/volumenes/caches)

---

## Hechos clave
- No se generan embeddings dentro de este repo: se importan externamente.
- Qdrant se usa para catalogo y ranking por similitud.
- La recomendacion final se sirve segun perfil autenticado del cliente.

---

## Matriz de validacion y persistencia (obligatoria)

### Suites verificadas
- Activas: `services/auth-service/tests`, `services/profile-service/tests`, `services/integration-service/tests`.
- Backup: `Fase1/_backup_phase1_base/phase1_auth-service/tests`, `Fase2/_backup_phase2_base/phase2_profile-service/tests`, `Fase6/_backup_phase6_base/phase6_integration-service/tests`.

### Persistencia por tipo de prueba
- Auth unit tests: memoria (fake repository).
- Profile unit tests: memoria (fake repository + fake storage ETL).
- Integration unit tests: memoria (fake vector store).
- Smoke test (`scripts/phase6_smoke_test.sh`): persistencia real en Qdrant con datos simulados + resumen `/tmp/phase6-smoke-summary.json`.

### Ejecucion recomendada
- Ejecutar pytest por ruta de suite para evitar colisiones de import entre backups y servicios activos.

### Frontend readiness
- Se documentan como backlog los endpoints recomendados: detalle de oferta, estado de vector de perfil, paginacion real y explicacion de score.
