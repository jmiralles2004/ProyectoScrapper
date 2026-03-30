# Integracion de Datos Externos (Ofertas y Vectores)

Este documento indica exactamente donde inyectar la informacion que viene de sistemas externos.

## 1) Donde entran las ofertas externas

Endpoint de entrada:
- `POST /integration/offers/import`

Archivo de contrato (schema):
- `services/integration-service/app/schemas.py`
- Modelo: `OfferImportItem`

Campos esperados por oferta:
- `offer_id`: id externo estable de la oferta
- `title`: titulo
- `company`: empresa
- `description`: descripcion
- `location`: ubicacion (opcional)
- `apply_url`: URL de candidatura (opcional)
- `vector`: embedding de la oferta (obligatorio)
- `metadata`: bloque libre de proveedor externo (opcional)

Mapeo a dominio interno:
- `services/integration-service/app/main.py`
- Funcion endpoint: `import_offers`
- Se transforma cada item a `OfferVectorRecord` y se envia al servicio de negocio

Persistencia final en base vectorial:
- `services/integration-service/app/vectorstore/qdrant_store.py`
- Metodo: `upsert_offer`
- Coleccion: `QDRANT_COLLECTION_OFFERS` (por defecto `offer_vectors`)

## 2) Donde entran los vectores de perfil externos

Endpoint de entrada:
- `POST /integration/profiles/import-vector`

Archivo de contrato (schema):
- `services/integration-service/app/schemas.py`
- Modelo: `ProfileVectorImportRequest`

Campos esperados:
- `user_id`: UUID del usuario (debe corresponder al mismo user_id del JWT de auth)
- `vector`: embedding del perfil
- `metadata`: bloque libre opcional

Persistencia final en base vectorial:
- `services/integration-service/app/vectorstore/qdrant_store.py`
- Metodo: `upsert_profile_vector`
- Coleccion: `QDRANT_COLLECTION_PROFILES` (por defecto `profile_vectors`)

## 3) Donde se consumen para recomendar ofertas

Endpoint de salida:
- `GET /integration/offers/recommended`

Flujo interno:
1. Extrae `user_id` desde JWT (`Authorization: Bearer <token>`)
2. Lee vector de perfil en `get_profile_vector`
3. Ejecuta busqueda vectorial en ofertas (`search_offers`)
4. Devuelve ranking por similitud

Archivos clave:
- `services/integration-service/app/dependencies.py`
- `services/integration-service/app/services/integration.py`
- `services/integration-service/app/vectorstore/qdrant_store.py`

## 4) Reglas criticas para datos reales

1. Dimension del vector:
- Debe coincidir exactamente con `INTEGRATION_VECTOR_SIZE`.
- Si no coincide, el endpoint devolvera `400`.

2. Valores del vector:
- Deben ser numericos y finitos.
- NaN/Infinity se rechazan con `400`.

3. IDs de oferta en Qdrant:
- Qdrant requiere point IDs tipo UUID o entero.
- El servicio transforma `offer_id` externo a UUID deterministico internamente.

4. Seguridad de ingesta:
- Si `INTEGRATION_INGEST_API_KEY` tiene valor, se debe enviar header `x-internal-api-key`.

## 5) Script recomendado de validacion y limpieza

Validar comportamiento tecnico con datos simulados:
- `scripts/phase6_smoke_test.sh`

Eliminar datos simulados + contenedores + volumenes del proyecto:
- `scripts/cleanup_fake_phase6_data.sh`

## 6) Checklist de conexion con proveedor externo

- El proveedor externo envia ofertas al endpoint de import.
- El proveedor externo envia vectores de perfil al endpoint de import.
- Se alinea `user_id` entre auth y proveedor de vectores.
- Se configura `INTEGRATION_VECTOR_SIZE` con la misma dimension del proveedor.
- Se configura `INTEGRATION_INGEST_API_KEY` en entornos no locales.

## 7) Readiness de consumo frontend (backlog)

Para facilitar integracion frontend productiva, se recomienda planificar estos endpoints adicionales:

- `GET /integration/offers/{offer_id}` para detalle de oferta.
- `GET /integration/profiles/vector-status` para saber si el usuario ya tiene vector importado.
- Paginacion real (`offset/cursor`) en catalogo y recomendadas.
- Endpoint de explicacion de score para transparencia de ranking.

Importante:
- Estos endpoints se documentan como backlog recomendado, no como funcionalidades activas en esta fase.
