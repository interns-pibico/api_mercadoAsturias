from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.models import Municipio, Categoria, Producto, Comercio
from app.schemas.schemas import (
    MunicipioOut, CategoriaOut, ProductoOut,
    ComercioOut, ComercioResumen
)

router = APIRouter()


# ── Municipios ─────────────────────────────────────────────
@router.get("/municipios", response_model=list[MunicipioOut], tags=["Municipios"])
def listar_municipios(db: Session = Depends(get_db)):
    return db.query(Municipio).order_by(Municipio.nombre).all()


@router.get("/municipios/{slug}", response_model=MunicipioOut, tags=["Municipios"])
def detalle_municipio(slug: str, db: Session = Depends(get_db)):
    m = db.query(Municipio).filter(Municipio.slug == slug).first()
    if not m:
        raise HTTPException(404, "Municipio no encontrado")
    return m


# ── Categorías ─────────────────────────────────────────────
@router.get("/categorias", response_model=list[CategoriaOut], tags=["Categorías"])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(Categoria).order_by(Categoria.nombre).all()


# ── Productos por categoría ────────────────────────────────
@router.get("/categorias/{slug}/productos", response_model=list[ProductoOut], tags=["Productos"])
def productos_por_categoria(slug: str, db: Session = Depends(get_db)):
    cat = db.query(Categoria).filter(Categoria.slug == slug).first()
    if not cat:
        raise HTTPException(404, "Categoría no encontrada")
    return db.query(Producto).filter(Producto.categoria_id == cat.id).all()


# ── Comercios ──────────────────────────────────────────────
@router.get("/municipios/{municipio_slug}/comercios", response_model=list[ComercioResumen], tags=["Comercios"])
def comercios_por_municipio(municipio_slug: str, db: Session = Depends(get_db)):
    m = db.query(Municipio).filter(Municipio.slug == municipio_slug).first()
    if not m:
        raise HTTPException(404, "Municipio no encontrado")
    return (
        db.query(Comercio)
        .filter(Comercio.municipio_id == m.id, Comercio.activo == True)
        .options(joinedload(Comercio.municipio))
        .all()
    )


@router.get("/municipios/{municipio_slug}/categorias/{categoria_slug}/comercios",
            response_model=list[ComercioResumen], tags=["Comercios"])
def comercios_por_municipio_y_categoria(
    municipio_slug: str, categoria_slug: str, db: Session = Depends(get_db)
):
    """Comercios activos en un municipio que venden productos de una categoría."""
    m = db.query(Municipio).filter(Municipio.slug == municipio_slug).first()
    if not m:
        raise HTTPException(404, "Municipio no encontrado")
    cat = db.query(Categoria).filter(Categoria.slug == categoria_slug).first()
    if not cat:
        raise HTTPException(404, "Categoría no encontrada")

    comercios = (
        db.query(Comercio)
        .join(Comercio.productos)
        .filter(
            Comercio.municipio_id == m.id,
            Comercio.activo == True,
            Producto.categoria_id == cat.id,
        )
        .options(joinedload(Comercio.municipio))
        .distinct()
        .all()
    )
    return comercios


@router.get("/productos/{producto_slug}/comercios", response_model=list[ComercioResumen], tags=["Comercios"])
def comercios_por_producto(producto_slug: str, db: Session = Depends(get_db)):
    """Todos los comercios activos que venden un producto concreto."""
    p = db.query(Producto).filter(Producto.slug == producto_slug).first()
    if not p:
        raise HTTPException(404, "Producto no encontrado")
    return [c for c in p.comercios if c.activo]


@router.get("/comercios/{slug}", response_model=ComercioOut, tags=["Comercios"])
def detalle_comercio(slug: str, db: Session = Depends(get_db)):
    c = (
        db.query(Comercio)
        .filter(Comercio.slug == slug, Comercio.activo == True)
        .options(joinedload(Comercio.municipio), joinedload(Comercio.productos))
        .first()
    )
    if not c:
        raise HTTPException(404, "Comercio no encontrado")
    return c