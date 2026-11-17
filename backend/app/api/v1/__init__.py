from fastapi import APIRouter

from app.api.v1.health import router as health_router
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

router = APIRouter(prefix="/api/v1")
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(households_router)
router.include_router(salary_router)
router.include_router(transactions_router)
router.include_router(documents_router)
router.include_router(wealth_router)
router.include_router(analytics_router)
router.include_router(assistant_router)
router.include_router(planning_router)
router.include_router(pf_router)
