"""
Script de seed: carga los 78 concejos de Asturias y datos de ejemplo.
Uso: python scripts/seed.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine, Base
from app.models.models import Municipio, Categoria, Producto, Comercio, comercio_productos
from slugify import slugify

Base.metadata.create_all(bind=engine)

CONCEJOS = [
    ("Gijón", 43.5453, -5.6615),
    ("Oviedo", 43.3614, -5.8593),
    ("Avilés", 43.5547, -5.9248),
    ("Siero", 43.3893, -5.6598),
    ("Langreo", 43.3003, -5.6866),
    ("Mieres", 43.2508, -5.7747),
    ("Castrillón", 43.5661, -5.9986),
    ("Carreño", 43.5561, -5.7769),
    ("Gozón", 43.6122, -5.8328),
    ("Villaviciosa", 43.4833, -5.4333),
    ("Llanes", 43.4199, -4.7549),
    ("Cangas de Onís", 43.3508, -5.1294),
    ("Tineo", 43.3314, -6.4178),
    ("Valdés", 43.5667, -6.5167),
    ("El Franco", 43.5667, -6.8333),
    ("Tapia de Casariego", 43.5667, -6.95),
    ("Coaña", 43.5333, -6.7333),
    ("Navia", 43.55, -6.7167),
    ("Cudillero", 43.5622, -6.1483),
    ("Muros de Nalón", 43.5383, -6.0758),
    ("Pravia", 43.4972, -6.1056),
    ("Soto del Barco", 43.5167, -6.05),
    ("Corvera de Asturias", 43.5525, -5.9839),
    ("Llanera", 43.4556, -5.8131),
    ("Las Regueras", 43.3833, -5.9167),
    ("Santo Adriano", 43.3333, -5.9667),
    ("Morcín", 43.2833, -5.85),
    ("Riosa", 43.2667, -5.9),
    ("Proaza", 43.2667, -5.9833),
    ("Teverga", 43.25, -6.05),
    ("Quirós", 43.2667, -5.9833),
    ("Lena", 43.15, -5.8167),
    ("Aller", 43.1833, -5.6833),
    ("Laviana", 43.2333, -5.5667),
    ("San Martín del Rey Aurelio", 43.2667, -5.6167),
    ("Caso", 43.2, -5.4833),
    ("Sobrescobio", 43.2333, -5.4667),
    ("Ponga", 43.2667, -5.1667),
    ("Amieva", 43.3, -5.1667),
    ("Piloña", 43.35, -5.4167),
    ("Nava", 43.3667, -5.5),
    ("Sariego", 43.4, -5.5667),
    ("Bimenes", 43.3333, -5.6167),
    ("Cabranes", 43.4167, -5.5333),
    ("Colunga", 43.4833, -5.2833),
    ("Caravia", 43.45, -5.2167),
    ("Ribadesella", 43.4667, -5.0667),
    ("Parres", 43.35, -5.2167),
    ("Onís", 43.3167, -5.05),
    ("Peñamellera Alta", 43.3, -4.7333),
    ("Peñamellera Baja", 43.35, -4.65),
    ("Ribadedeva", 43.3833, -4.5667),
    ("Cobreces", 43.2167, -4.5167),
    ("Cabrales", 43.2833, -4.8833),
    ("Cangas del Narcea", 43.1667, -6.55),
    ("Degaña", 43.0667, -6.5167),
    ("Ibias", 43.0167, -6.7833),
    ("Allande", 43.2333, -6.6167),
    ("Grandas de Salime", 43.2167, -6.8667),
    ("Pesoz", 43.2167, -6.9167),
    ("San Martín de Oscos", 43.25, -7.05),
    ("Santa Eulalia de Oscos", 43.2333, -7.1167),
    ("Villanueva de Oscos", 43.2833, -7.1),
    ("Vegadeo", 43.4667, -7.0333),
    ("Taramundi", 43.3667, -7.1),
    ("San Tirso de Abres", 43.4, -7.05),
    ("Castropol", 43.5167, -7.0333),
    ("Boal", 43.45, -6.8333),
    ("Illano", 43.3333, -6.9167),
    ("Villayón", 43.3667, -6.75),
    ("Salas", 43.4167, -6.25),
    ("Belmonte de Miranda", 43.2833, -6.25),
    ("Grado", 43.3833, -6.0667),
    ("Candamo", 43.4333, -6.05),
    ("Pravia", 43.4972, -6.1056),
    ("Muñás de Arriba", 43.4333, -6.2),
    ("Yernes y Tameza", 43.2333, -6.05),
    ("Miranda", 43.45, -6.2167),
]

CATEGORIAS = [
    ("Gastro", "gastro", "🧀", "Productos gastronómicos asturianos: quesos, embutidos, conservas..."),
    ("Dulce", "dulce", "🍰", "Repostería y dulces tradicionales"),
    ("Sidra y Bebidas", "sidra-bebidas", "🍺", "Sidra natural, vinos y otras bebidas locales"),
    ("Artesanía", "artesania", "🎨", "Productos artesanales y de diseño local"),
    ("Huerta y Campo", "huerta-campo", "🌿", "Frutas, verduras y productos de la tierra"),
]

PRODUCTOS = [
    # Gastro
    ("Queso Afuega'l Pitu", "gastro", "Queso tradicional asturiano de pasta blanda"),
    ("Queso Cabrales", "gastro", "Queso azul con denominación de origen protegida"),
    ("Chorizo asturiano", "gastro", "Embutido ahumado tradicional"),
    ("Morcilla asturiana", "gastro", "Morcilla tradicional con arroz y especias"),
    ("Conservas de bonito", "gastro", "Bonito del norte en aceite de oliva"),
    # Dulce
    ("Carbayones", "dulce", "Pastel típico de Oviedo con almendra y yema"),
    ("Casadielles", "dulce", "Empanadilla frita rellena de nuez y anís"),
    ("Arroz con leche", "dulce", "Postre tradicional asturiano gratinado"),
    # Sidra
    ("Sidra natural", "sidra-bebidas", "Sidra asturiana sin gas, de manzana autóctona"),
    ("Sidra espumosa", "sidra-bebidas", "Sidra achampanada para ocasiones especiales"),
    # Artesanía
    ("Cerámica asturiana", "artesania", "Piezas de barro pintadas a mano"),
    ("Madera tallada", "artesania", "Figuras y utensilios en madera de castaño"),
    # Huerta
    ("Manzana asturiana", "huerta-campo", "Variedades autóctonas para sidra y mesa"),
    ("Faba asturiana", "huerta-campo", "Legumbre con denominación de origen protegida"),
    ("Escanda", "huerta-campo", "Cereal ancestral asturiano, sin gluten"),
]


def seed():
    db = SessionLocal()
    try:
        # Municipios
        if db.query(Municipio).count() == 0:
            seen = set()
            for nombre, lat, lon in CONCEJOS:
                if nombre in seen:
                    continue
                seen.add(nombre)
                db.add(Municipio(nombre=nombre, slug=slugify(nombre), lat=lat, lon=lon))
            db.commit()
            print(f"✅ {len(seen)} municipios insertados")
        else:
            print("⏭ Municipios ya existen")

        # Categorías
        if db.query(Categoria).count() == 0:
            for nombre, slug, icono, desc in CATEGORIAS:
                db.add(Categoria(nombre=nombre, slug=slug, icono=icono, descripcion=desc))
            db.commit()
            print(f"✅ {len(CATEGORIAS)} categorías insertadas")

        # Productos
        if db.query(Producto).count() == 0:
            cats = {c.slug: c for c in db.query(Categoria).all()}
            for nombre, cat_slug, desc in PRODUCTOS:
                db.add(Producto(
                    nombre=nombre,
                    slug=slugify(nombre),
                    descripcion=desc,
                    categoria_id=cats[cat_slug].id,
                ))
            db.commit()
            print(f"✅ {len(PRODUCTOS)} productos insertados")

        # Comercio de ejemplo
        if db.query(Comercio).count() == 0:
            gijon = db.query(Municipio).filter(Municipio.slug == "gijon").first()
            queso = db.query(Producto).filter(Producto.slug == "queso-cabralles").first()
            sidra = db.query(Producto).filter(Producto.slug == "sidra-natural").first()
            prods = [p for p in [queso, sidra] if p]

            c = Comercio(
                nombre="La Tienda Asturiana",
                slug="la-tienda-asturiana-gijon",
                descripcion="Especialistas en productos típicos de Asturias desde 1985",
                direccion="Calle Corrida, 12, Gijón",
                lat=43.5453,
                lon=-5.6615,
                telefono="985 000 000",
                web="https://ejemplo.com",
                horario="Lun-Sáb 10:00-20:00",
                municipio_id=gijon.id if gijon else 1,
                activo=True,
                productos=prods,
            )
            db.add(c)
            db.commit()
            print("✅ Comercio de ejemplo insertado")

        print("\n🎉 Seed completado")
    finally:
        db.close()


if __name__ == "__main__":
    seed()