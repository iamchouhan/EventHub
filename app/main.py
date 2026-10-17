from fastapi import FastAPI

from app.routers.events import router as events_router

app = FastAPI(
    title="EventHub API",
    description="Enterprise event and content management backend",
    version="0.1.0",
)

app.include_router(events_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}