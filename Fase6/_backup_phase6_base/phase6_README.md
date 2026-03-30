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
