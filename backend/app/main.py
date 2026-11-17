from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.health import database_health_check, health_check
from app.api.v1.auth import router as auth_router
from app.api.v1.households import router as households_router
from app.api.v1.salary import router as salary_router
from app.api.v1.transactions import router as transactions_router
from app.api.v1.documents import router as documents_router
from app.api.v1.wealth import router as wealth_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.planning import router as planning_router
from app.api.v1.pf import router as pf_router
from app.api.v1.notifications import router as notifications_router
from app.core.config import get_settings
from app.core.errors import validation_exception_handler
from app.core.logging import configure_logging
from app.core.security_middleware import RateLimitMiddleware, SecurityHeadersMiddleware
from app.schemas.health import HealthResponse


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.app_env != "production" else None,
        redoc_url="/redoc" if settings.app_env != "production" else None,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(RateLimitMiddleware)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_api_route("/api/v1/health", health_check, methods=["GET"], response_model=HealthResponse, tags=["health"])
    application.add_api_route("/api/v1/health/database", database_health_check, methods=["GET"], response_model=HealthResponse, tags=["health"])
    for route_group in (auth_router, households_router, salary_router, transactions_router, documents_router, wealth_router, analytics_router, assistant_router, planning_router, pf_router, notifications_router):
        for route in route_group.routes:
            application.add_api_route(
                f"/api/v1{route.path}", route.endpoint, methods=list(route.methods or []),
                response_model=route.response_model, status_code=route.status_code,
                tags=route.tags,
            )
    # Backward-compatible aliases during the foundation phase.
    application.add_api_route("/health", health_check, methods=["GET"], response_model=HealthResponse, tags=["health"])
    application.add_api_route("/health/database", database_health_check, methods=["GET"], response_model=HealthResponse, tags=["health"])
    return application


app = create_app()
