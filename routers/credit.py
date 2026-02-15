from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from models.schemas import CreditRequest
from models.schemas import CreditResponse
from services.interfaces import IFinancialCalculator


router = APIRouter()


@router.post("/", response_model=CreditResponse)
async def calculate_credit(
        request_body: CreditRequest,
        request: Request
    ) -> CreditRequest | HTTPException:
    """Расчет потребительского кредита

    - **amount**: Сумма кредита
    - **years**: Срок в годах (0.25-30)
    - **rate**: Годовая процентная ставка (0-99%)
    - **payment_type**: Тип платежа
    - **commission**: Комиссия в % от суммы
    - **insurance**: Страховка в % годовых
    """
    try:
        fin_calc: IFinancialCalculator = request.app.state.services.fin_calc
        return fin_calc.calculate_credit(request_body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
