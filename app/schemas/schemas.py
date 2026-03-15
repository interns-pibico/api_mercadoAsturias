from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ── Municipio ──────────────────────────────────────────────
class MunicipioBase(BaseModel):
    nombre: str
    slug: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    provincia: str = "Asturias"

class MunicipioOut(MunicipioBase):
    id: int
    model_config = {"from_attributes": True}


# ── Categoria ──────────────────────────────────────────────
class CategoriaBase(BaseModel):
    nombre: str
    slug: str
    descripcion: Optional[str] = None
    icono: Optional[str] = None

class CategoriaOut(CategoriaBase):
    id: int
    model_config = {"from_attributes": True}


# ── Producto ───────────────────────────────────────────────
class ProductoBase(BaseModel):
    nombre: str
    slug: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None

class ProductoOut(ProductoBase):
    id: int
    categoria: CategoriaOut
    model_config = {"from_attributes": True}

class ProductoSimple(BaseModel):
    id: int
    nombre: str
    slug: str
    model_config = {"from_attributes": True}


# ── Comercio ───────────────────────────────────────────────
class ComercioBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    direccion: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    telefono: Optional[str] = None
    web: Optional[str] = None
    horario: Optional[str] = None

class ComercioOut(ComercioBase):
    id: int
    slug: str
    activo: bool
    municipio: MunicipioOut
    productos: list[ProductoSimple] = []
    suscripcion_hasta: Optional[datetime] = None
    model_config = {"from_attributes": True}

class ComercioResumen(BaseModel):
    """Vista compacta para listados"""
    id: int
    nombre: str
    slug: str
    direccion: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    telefono: Optional[str] = None
    web: Optional[str] = None
    horario: Optional[str] = None
    municipio: MunicipioOut
    model_config = {"from_attributes": True}


# ── Admin: creación/edición ────────────────────────────────
class ComercioCreate(ComercioBase):
    nombre: str
    municipio_id: int
    producto_ids: list[int] = []

class CategoriaCreate(CategoriaBase):
    pass

class ProductoCreate(ProductoBase):
    categoria_id: int

class MunicipioCreate(MunicipioBase):
    pass