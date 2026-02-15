from __future__ import annotations

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from routers import compare
from routers import credit
from routers import goal
from routers import montecarlo
from routers import mortgage
from routers import savings
from services.v1 import CompareService
from services.v1 import FinancialCalculator
from services.v1 import MonteCarloService


app = FastAPI(
    title="FinSimulator API",
    description="Финансовый калькулятор для расчетов кредитов, вкладов и инвестиций",
    version="1.0.0",
)

app.state.services = SimpleNamespace(
    fin_calc=FinancialCalculator(),
    montecarlo_service=MonteCarloService(),
    cmp_service=CompareService(),
)


app.include_router(mortgage.router, prefix="/api/v1/mortgage", tags=["Ипотека"])
app.include_router(savings.router, prefix="/api/v1/savings", tags=["Накопления"])
app.include_router(credit.router, prefix="/api/v1/credit", tags=["Кредиты"])
app.include_router(goal.router, prefix="/api/v1/goal", tags=["Цели"])
app.include_router(montecarlo.router, prefix="/api/v1/montecarlo", tags=["Монте-Карло"])
app.include_router(compare.router, prefix="/api/v1/compare", tags=["Сравнение"])


@app.get("/", response_class=HTMLResponse)
async def root() -> HTMLResponse:
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FinSimulator API</title>
    </head>
    <body>
        <div class="container">
            <h1>FinSimulator API</h1>
            
            <h2>Основные эндпоинты:</h2>
            <ul>
                <li><b><code>GET /api/mortgage</code></b> - 
                    симуляция ипотечных расчетов
                </li>
                <li><b><code>GET /api/savings</code></b> - 
                    расчет накоплений и депозитов
                </li>
                <li><b><code>GET /api/credit</code></b> - 
                    кредитные калькуляторы
                </li>
                <li><b><code>GET /api/goal</code></b> - 
                    планирование финансовых целей
                </li>
                <li><b><code>GET /api/montecarlo</code></b> - 
                    метод Монте-Карло для финансового моделирования
                </li>
                <li><b><code>GET /api/compare</code></b> - 
                    сравнение финансовых стратегий
                </li>
            </ul>
            
            <h2>Технические эндпоинты:</h2>
            <ul>
                <li><strong><a href="/health">/health</a></strong> - 
                    проверка работоспособности API
                </li>
                <li><strong><a href="/docs">/docs</a></strong> - 
                    интерактивная документация Swagger
                </li>
                <li><strong><a href="/redoc">/redoc</a></strong> - 
                    альтернативная документация ReDoc
                </li>
            </ul>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health", response_model=None)
async def health_check() -> dict[str, any]:
    """Проверка работоспособности API"""
    from datetime import datetime

    return {
        "status": "healthy",
        "timestamp": datetime.now().astimezone(),
    }
