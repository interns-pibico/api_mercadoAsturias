from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.routers.public import router as public_router
from app.admin.admin import router as admin_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    root_path="/mercado",
    docs_url=f"/v1/docs",
    redoc_url=f"/v1/redoc",
    openapi_url=f"/v1/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia por tu dominio en producción
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(public_router, prefix="/v1")
app.include_router(admin_router)


@app.get("/", tags=["Info"])
def root():
    return {
        "nombre": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "docs": "/v1/docs",
        "admin": "/admin/",
    }