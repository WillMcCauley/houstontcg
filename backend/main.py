from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.analytics import router as analytics_router
from backend.routes.chat import router as chat_router
from backend.routes.feedback import router as feedback_router
from backend.routes.products import router as products_router


app = FastAPI(
    title="Houston TCG AI Sales and Support Copilot",
    version="1.0.0",
    description=(
        "Production-style sales and support copilot API for Houston TCG. "
        "Provides intent classification, semantic product search, policy retrieval, "
        "recommendation logic, and interaction analytics."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(chat_router)
app.include_router(analytics_router)
app.include_router(feedback_router)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
