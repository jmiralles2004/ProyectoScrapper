# Integration Service (Fase 6)

FastAPI service that ingests offers/profile vectors and returns personalized offer recommendations using a vector database.

## Endpoints
- GET /health
- GET /integration/health
- POST /integration/offers/import
- POST /integration/profiles/import-vector
- GET /integration/offers/catalog
- GET /integration/offers/recommended

## Minimum environment variables
- QDRANT_URL
- JWT_SECRET
- JWT_ALGORITHM
- INTEGRATION_VECTOR_SIZE
- QDRANT_COLLECTION_PROFILES
- QDRANT_COLLECTION_OFFERS
- INTEGRATION_INGEST_API_KEY (optional)

## Run local API
uvicorn app.main:create_app --factory --reload --port 8002

## Tests
pytest tests/test_integration.py -v
