from fastapi import FastAPI
from .routers import calendar_router

app = FastAPI(title="Macro Calendar API")

# Inclui todas as rotas definidas no módulo calendar_router.py
app.include_router(calendar_router.router)


@app.get("/")
def root():
    """
    Endpoint raiz — útil pra verificar se a API está ativa.
    """
    return {
        "message": "Macro Calendar API is running.",
        "routes": [
            "/events (filtros combináveis)",
            "/country/{country_iso3}",
            "/categories",
            "/docs (Swagger UI)"
        ],
    }
