from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, Float,
    DateTime, ForeignKey, Table, Text
)
from sqlalchemy.orm import relationship
from app.core.database import Base


# Tabla intermedia: qué comercio vende qué producto
comercio_productos = Table(
    "comercio_productos",
    Base.metadata,
    Column("comercio_id", Integer, ForeignKey("comercios.id"), primary_key=True),
    Column("producto_id", Integer, ForeignKey("productos.id"), primary_key=True),
)


class Municipio(Base):
    __tablename__ = "municipios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    lat = Column(Float)
    lon = Column(Float)
    provincia = Column(String(100), default="Asturias")

    comercios = relationship("Comercio", back_populates="municipio")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    descripcion = Column(Text)
    icono = Column(String(10))  # emoji o nombre de icono

    productos = relationship("Producto", back_populates="categoria")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    descripcion = Column(Text)
    imagen_url = Column(String(300))
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)

    categoria = relationship("Categoria", back_populates="productos")
    comercios = relationship("Comercio", secondary=comercio_productos, back_populates="productos")


class Comercio(Base):
    __tablename__ = "comercios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    descripcion = Column(Text)
    direccion = Column(String(250))
    lat = Column(Float)
    lon = Column(Float)
    telefono = Column(String(20))
    web = Column(String(250))
    horario = Column(Text)
    municipio_id = Column(Integer, ForeignKey("municipios.id"), nullable=False)
    activo = Column(Boolean, default=False)  # se activa cuando paga
    api_key = Column(String(64), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    suscripcion_hasta = Column(DateTime, nullable=True)

    municipio = relationship("Municipio", back_populates="comercios")
    productos = relationship("Producto", secondary=comercio_productos, back_populates="comercios")