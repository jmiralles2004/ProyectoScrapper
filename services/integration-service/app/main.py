"""FastAPI entrypoint for the Phase 6 integration service."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.openapi.docs import get_swagger_ui_html

from .core.config import Settings, get_settings
from .dependencies import (
    get_current_user_id,
    get_integration_service,
    verify_ingest_api_key,
)
from .models import OfferVectorRecord
from .schemas import (
    HealthResponse,
    OfferCatalogResponse,
    OfferResponse,
    OffersImportRequest,
    OffersImportResponse,
    ProfileVectorImportRequest,
    ProfileVectorImportResponse,
    RecommendedOffersResponse,
)
from .services.integration import (
    IntegrationService,
    IntegrationServiceError,
    InvalidVectorError,
    ProfileVectorNotFoundError,
)
from .vectorstore.qdrant_store import QdrantIntegrationVectorStore


def _to_offer_response(record: OfferVectorRecord) -> OfferResponse:
    """Map a domain offer record into API response format."""

    return OfferResponse(
        offer_id=record.offer_id,
        title=record.title,
        company=record.company,
        description=record.description,
        location=record.location,
        apply_url=record.apply_url,
        metadata=record.metadata,
        score=record.score,
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the integration service application."""

    resolved_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        """Prepare and tear down application resources."""

        if not hasattr(application.state, "vector_store"):
            application.state.vector_store = QdrantIntegrationVectorStore(
                qdrant_url=resolved_settings.qdrant_url,
                vector_size=resolved_settings.integration_vector_size,
                profile_collection=resolved_settings.qdrant_collection_profiles,
                offer_collection=resolved_settings.qdrant_collection_offers,
            )

        application.state.vector_store.ensure_collections()

        if not hasattr(application.state, "integration_service"):
            application.state.integration_service = IntegrationService(
                vector_store=application.state.vector_store,
                expected_vector_size=resolved_settings.integration_vector_size,
                offer_collection=resolved_settings.qdrant_collection_offers,
                profile_collection=resolved_settings.qdrant_collection_profiles,
            )

        yield

    app = FastAPI(
        title="JobMatch Integration Service",
        version="1.0.0",
        lifespan=lifespan,
        description=(
            "Servicio de integracion de vectores y recomendacion semantica.\n\n"
            "Permite: \n"
            "- Importar ofertas vectorizadas\n"
            "- Importar vector de perfil de usuario\n"
            "- Consultar catalogo de ofertas\n"
            "- Obtener recomendaciones por similitud"
        ),
    )
    app.state.settings = resolved_settings

    health_description = (
        "Verifica que el integration-service esta activo y operativo.\n\n"
        "No requiere autenticacion y se usa para healthchecks de infraestructura."
    )

    import_offers_description = (
        "Importa un lote de ofertas con su embedding vectorial.\n\n"
        "- Uso esperado: integracion interna (ETL o proveedor externo).\n"
        "- Si hay API key configurada, requiere header `x-internal-api-key`.\n"
        "- Cada vector debe tener exactamente el tamano configurado en el servicio."
    )

    import_profile_vector_description = (
        "Registra o actualiza el vector de perfil de un usuario.\n\n"
        "- Si hay API key configurada, requiere header `x-internal-api-key`.\n"
        "- Este vector se usa despues para recomendaciones personalizadas."
    )

    catalog_description = (
        "Lista ofertas almacenadas en la base vectorial sin ranking por usuario.\n\n"
        "- Endpoint de catalogo/inspeccion operativa.\n"
        "- Si hay API key configurada, requiere header `x-internal-api-key`."
    )

    recommended_description = (
        "Devuelve ofertas recomendadas para el usuario autenticado.\n\n"
        "- Requiere token Bearer (`Authorization: Bearer <token>`).\n"
        "- Busca similitud entre vector de perfil del usuario y vectores de ofertas.\n"
        "- Si el usuario no tiene vector de perfil, devuelve 404."
    )

    @app.get(
        "/health",
        response_model=HealthResponse,
        summary="Verificar estado del integration-service",
        description=health_description,
        tags=["Health"],
    )
    @app.get(
        "/integration/health",
        response_model=HealthResponse,
        summary="Verificar estado del integration-service (prefijo integration)",
        description=health_description,
        tags=["Health"],
    )
    async def health() -> HealthResponse:
        """Return a basic healthcheck payload."""

        return HealthResponse(status="ok", service=resolved_settings.service_name)

    @app.post(
        "/integration/offers/import",
        response_model=OffersImportResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Importar lote de ofertas vectorizadas",
        description=import_offers_description,
        responses={
            400: {"description": "Vector invalido (vacio, tamano incorrecto o no finito)"},
            401: {"description": "x-internal-api-key invalida cuando esta configurada"},
            422: {"description": "Payload invalido"},
            502: {"description": "Fallo al persistir datos en la base vectorial"},
        },
        tags=["Integration Ingest"],
    )
    async def import_offers(
        payload: OffersImportRequest,
        _: None = Depends(verify_ingest_api_key),
        integration_service: IntegrationService = Depends(get_integration_service),
    ) -> OffersImportResponse:
        """Import offers and vectors received from an external provider."""

        import_items: list[tuple[OfferVectorRecord, list[float]]] = []
        for offer in payload.offers:
            import_items.append(
                (
                    OfferVectorRecord(
                        offer_id=offer.offer_id,
                        title=offer.title,
                        company=offer.company,
                        description=offer.description,
                        location=offer.location,
                        apply_url=offer.apply_url,
                        metadata=offer.metadata,
                    ),
                    offer.vector,
                )
            )

        try:
            imported_count = integration_service.import_offers(import_items)
        except InvalidVectorError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except IntegrationServiceError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

        return OffersImportResponse(
            imported_offers=imported_count,
            collection=integration_service.offer_collection,
            vector_size=integration_service.expected_vector_size,
        )

    @app.post(
        "/integration/profiles/import-vector",
        response_model=ProfileVectorImportResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Importar vector de perfil de usuario",
        description=import_profile_vector_description,
        responses={
            400: {"description": "Vector invalido (vacio, tamano incorrecto o no finito)"},
            401: {"description": "x-internal-api-key invalida cuando esta configurada"},
            422: {"description": "Payload invalido"},
            502: {"description": "Fallo al persistir el vector de perfil"},
        },
        tags=["Integration Ingest"],
    )
    async def import_profile_vector(
        payload: ProfileVectorImportRequest,
        _: None = Depends(verify_ingest_api_key),
        integration_service: IntegrationService = Depends(get_integration_service),
    ) -> ProfileVectorImportResponse:
        """Import one profile vector generated by an external embedding provider."""

        try:
            integration_service.import_profile_vector(
                user_id=payload.user_id,
                vector=payload.vector,
                metadata=payload.metadata,
            )
        except InvalidVectorError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except IntegrationServiceError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

        return ProfileVectorImportResponse(
            user_id=payload.user_id,
            collection=integration_service.profile_collection,
            vector_size=integration_service.expected_vector_size,
        )

    @app.get(
        "/integration/offers/catalog",
        response_model=OfferCatalogResponse,
        summary="Consultar catalogo de ofertas almacenadas",
        description=catalog_description,
        responses={
            401: {"description": "x-internal-api-key invalida cuando esta configurada"},
            502: {"description": "Fallo al consultar la base vectorial"},
        },
        tags=["Integration Catalog"],
    )
    async def get_offer_catalog(
        limit: int = Query(
            default=20,
            ge=1,
            le=100,
            description="Cantidad maxima de ofertas a devolver.",
        ),
        _: None = Depends(verify_ingest_api_key),
        integration_service: IntegrationService = Depends(get_integration_service),
    ) -> OfferCatalogResponse:
        """List available offers currently stored in the vector database."""

        try:
            offers = integration_service.list_offer_catalog(limit=limit)
        except IntegrationServiceError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

        return OfferCatalogResponse(
            collection=integration_service.offer_collection,
            total=len(offers),
            offers=[_to_offer_response(item) for item in offers],
        )

    @app.get(
        "/integration/offers/recommended",
        response_model=RecommendedOffersResponse,
        summary="Obtener ofertas recomendadas para el usuario autenticado",
        description=recommended_description,
        responses={
            401: {"description": "Falta token o token invalido/expirado"},
            404: {"description": "No existe vector de perfil para el usuario"},
            502: {"description": "Fallo al calcular recomendaciones"},
        },
        tags=["Integration Recommendations"],
    )
    async def get_recommended_offers(
        limit: int = Query(
            default=10,
            ge=1,
            le=50,
            description="Cantidad maxima de recomendaciones a devolver.",
        ),
        user_id=Depends(get_current_user_id),
        integration_service: IntegrationService = Depends(get_integration_service),
    ) -> RecommendedOffersResponse:
        """Return offers ranked by similarity for the authenticated user profile."""

        try:
            offers = integration_service.get_recommended_offers(user_id=user_id, limit=limit)
        except ProfileVectorNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except IntegrationServiceError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

        return RecommendedOffersResponse(
            user_id=user_id,
            collection=integration_service.offer_collection,
            total=len(offers),
            offers=[_to_offer_response(item) for item in offers],
        )

    @app.get("/integration/openapi.json", include_in_schema=False)
    async def integration_openapi() -> dict[str, Any]:
        """Expose OpenAPI schema through the /integration prefix for gateway usage."""

        return app.openapi()

    @app.get("/integration/docs", include_in_schema=False)
    async def integration_docs():
        """Expose Swagger UI through the /integration prefix for gateway usage."""

        return get_swagger_ui_html(
            openapi_url="/integration/openapi.json",
            title=f"{app.title} - Swagger UI",
        )

    return app
