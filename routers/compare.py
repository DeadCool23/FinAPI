from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from models.schemas import CompareRequest
from models.schemas import CompareResponse
from services.interfaces import ICompareService


router = APIRouter()


@router.post("/", response_model=CompareResponse)
async def compare_financial_products(
        request_body: CompareRequest,
        request: Request
    ) -> CompareResponse | HTTPException:
    """Сравнение финансовых продуктов"""
    try:
        cmp_service: ICompareService = request.app.state.services.cmp_service
        return cmp_service.comparison(request_body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
