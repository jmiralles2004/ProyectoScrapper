# Fase 6 - Integracion Final

## Objetivo
Dejar montada la integracion final para recoger ofertas y vectores de embeddings desde un proveedor externo y devolver recomendaciones segun el perfil del cliente.

## Que incluye
- Servicio FastAPI `integration-service`
- Importacion de ofertas con vector (`POST /integration/offers/import`)
- Importacion de vector de perfil (`POST /integration/profiles/import-vector`)
- Catalogo de ofertas desde base vectorial (`GET /integration/offers/catalog`)
- Recomendaciones por perfil autenticado (`GET /integration/offers/recommended`)
- Healthchecks (`/health` y `/integration/health`)
- Integracion con Qdrant como base vectorial
- Proteccion JWT para recomendaciones
- API key interna opcional para endpoints de ingesta

## Componentes
- `services/integration-service/` - Codigo y tests del servicio de integracion
- `docker-compose.yml` - Integracion de `integration-service`
- `nginx-proxy/nginx.conf` - Proxy de rutas `/integration/*`
- `.env` y `.env.docker` - Variables del servicio de integracion
- `endpoints.md` - Endpoints globales actualizados con Fase 6
- `explicacion-archivos.md` - Explicacion estructural de la fase
- `_backup_phase6_base/` - Copia inmune de referencia

## Criterio de fase completada
La fase se considera lista cuando el servicio arranca con Docker, acepta importacion de ofertas/vectores externos y devuelve ofertas recomendadas en base al perfil del cliente.

## Integracion con proveedor externo
- Guia exacta de conexion de ofertas y vectores: `Fase6/INTEGRACION_DATOS_EXTERNOS.md`
- Smoke test tecnico (datos simulados): `scripts/phase6_smoke_test.sh`
- Limpieza total de datos simulados/artefactos Docker: `scripts/cleanup_fake_phase6_data.sh`

## Smoke test (datos simulados)
Las pruebas de esta fase se hacen con datos falsos/simulados para validar comportamiento tecnico.

Que valida este smoke test:
- Que los endpoints responden correctamente.
- Que la ingesta guarda ofertas y vectores.
- Que el catalogo devuelve datos importados.
- Que la recomendacion devuelve ranking para un perfil con vector.

Que NO valida:
- Calidad real de matching en produccion.
- Calidad real de embeddings del proveedor externo.
- Relevancia final de negocio.

Comandos de ejemplo:
```bash
# 1) Healthcheck
curl http://localhost/integration/health

# 2) Importar ofertas simuladas (x-internal-api-key si esta configurada)
curl -X POST http://localhost/integration/offers/import \
	-H "x-internal-api-key: <internal-key>" \
	-H "Content-Type: application/json" \
	-d '{
		"offers": [
			{
				"offer_id": "test-offer-1",
				"title": "Backend Developer TEST",
				"company": "FakeCorp",
				"description": "Oferta simulada para smoke test",
				"vector": [0.11, 0.12, 0.13, 0.14]
			}
		]
	}'

# 3) Importar vector de perfil simulado
curl -X POST http://localhost/integration/profiles/import-vector \
	-H "x-internal-api-key: <internal-key>" \
	-H "Content-Type: application/json" \
	-d '{
		"user_id": "11111111-1111-1111-1111-111111111111",
		"vector": [0.11, 0.12, 0.13, 0.14]
	}'

# 4) Catalogo
curl -H "x-internal-api-key: <internal-key>" "http://localhost/integration/offers/catalog?limit=10"

# 5) Recomendadas (requiere JWT valido del user_id de prueba)
curl -H "Authorization: Bearer <token>" "http://localhost/integration/offers/recommended?limit=10"
```

Nota: para evitar errores de dimension, usa `scripts/phase6_smoke_test.sh`, que genera vectores con el tamaño real de `INTEGRATION_VECTOR_SIZE`.

## Validacion de tests (obligatorio)

Suites activas verificadas:
- `services/auth-service/tests`: OK.
- `services/profile-service/tests`: OK.
- `services/integration-service/tests`: OK.

Suites backup verificadas:
- `Fase1/_backup_phase1_base/phase1_auth-service/tests`: OK.
- `Fase2/_backup_phase2_base/phase2_profile-service/tests`: OK.
- `Fase6/_backup_phase6_base/phase6_integration-service/tests`: OK.

Smoke test E2E:
- `scripts/phase6_smoke_test.sh`: OK.

## Que se guarda en cada test (obligatorio)

- Auth unit tests: datos en memoria (repositorio fake), sin PostgreSQL real.
- Profile unit tests: datos en memoria (repo fake + storage fake), sin PostgreSQL/MinIO reales.
- Integration unit tests: datos en memoria (vector store fake), sin Qdrant real.
- Smoke test E2E: datos simulados persistidos en Qdrant real + resumen en `/tmp/phase6-smoke-summary.json`.

## Nota de ejecucion de pruebas

- No se recomienda `pytest -q` en la raiz del repo cuando conviven backups y servicios activos con el mismo nombre de modulo `app`.
- Ejecutar pytest por ruta de suite para evitar colisiones de import.

## Readiness frontend (pendientes recomendados)

No estan implementados todavia, pero se recomiendan para frontend productivo:
- `GET /integration/offers/{offer_id}` para vista detalle.
- `GET /integration/profiles/vector-status` para estado de vector de perfil.
- Paginacion real (`offset/cursor`) en catalogo y recomendadas.
- Endpoint de explicacion de score para trazabilidad UX.
