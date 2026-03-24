"""
Script de seed: carga los 77 concejos de Asturias y los datos reales de producción.
Uso: python scripts/seed.py
"""
import sys
import os
import secrets

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine, Base
from app.models.models import Municipio, Categoria, Producto, Comercio
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

# (nombre, slug, categoria_slug, descripcion)
PRODUCTOS = [
    # Gastro
    ("Queso Afuega'l Pitu", "queso-afuega-l-pitu", "gastro", "Queso tradicional asturiano de pasta blanda"),
    ("Queso Cabrales", "queso-cabrales", "gastro", "Queso azul con denominación de origen protegida"),
    ("Chorizo asturiano", "chorizo-asturiano", "gastro", "Embutido ahumado tradicional"),
    ("Morcilla asturiana", "morcilla-asturiana", "gastro", "Morcilla tradicional con arroz y especias"),
    ("Conservas de bonito", "conservas-de-bonito", "gastro", "Bonito del norte en aceite de oliva"),
    ("Queso Vidiago", "queso-vidiago", "gastro", "Queso de leche vacuna elaborado en la localidad Llanisca de Vidiago."),
    ("Queso tres leches de Pría", "queso-tres-leches-de-pria", "gastro", "Queso elaborado con leche de vaca, cabra y oveja. Producido en la localidad de Pría (Llanes)"),
    ("Miel Abeja", "miel-abeja", "gastro", None),
    ("Anchoas", "anchoas", "gastro", None),
    ("Queso Casín", "queso-casin", "gastro", "Queso elaborado en el concejo de Caso elaborado con leche entera y cruda de vaca."),
    ("Queso la Peral", "queso-la-peral", "gastro", None),
    # Dulce
    ("Carbayones", "carbayones", "dulce", "Pastel típico de Oviedo con almendra y yema"),
    ("Casadielles", "casadielles", "dulce", "Empanadilla frita rellena de nuez y anís"),
    ("Arroz con leche", "arroz-con-leche", "dulce", "Postre tradicional asturiano gratinado"),
    ("Moscovitas", "moscovitas", "dulce", "Dulce artesano a base de almendras, nata , harina y chocolate"),
    ("Carajitos  de avellana", "carajitos-de-avellana", "dulce", "Pastel típico asturiano elaborado a base de avellanas."),
    ("Marañueles", "maranueles", "dulce", None),
    # Sidra y Bebidas
    ("Sidra natural", "sidra-natural", "sidra-bebidas", "Sidra asturiana sin gas, de manzana autóctona"),
    ("Sidra espumosa", "sidra-espumosa", "sidra-bebidas", "Sidra achampanada para ocasiones especiales"),
    ("Cerveza Artesana", "cerveza-artesana", "sidra-bebidas", None),
    ("Aguardiente de Sidra", "aguardiente-de-sidra", "sidra-bebidas", "Producto destilado hecho a partir de la mejor selección de sidra asturiana, envejecido en barricas de roble."),
    ("Licor de avellanas", "licor-de-avellanas", "sidra-bebidas", None),
    # Artesanía
    ("Cerámica asturiana", "ceramica-asturiana", "artesania", "Piezas de barro pintadas a mano"),
    ("Madera tallada", "madera-tallada", "artesania", "Figuras y utensilios en madera de castaño"),
    ("cerámica", "ceramica", "artesania", None),
    # Huerta y Campo
    ("Manzana asturiana", "manzana-asturiana", "huerta-campo", "Variedades autóctonas para sidra y mesa"),
    ("Faba asturiana", "faba-asturiana", "huerta-campo", "Legumbre con denominación de origen protegida"),
    ("Escanda", "escanda", "huerta-campo", "Cereal ancestral asturiano, sin gluten"),
    ("Fabes verdinas", "fabes-verdinas", "huerta-campo", "Variedad gourmet de alubia pequeña, color verde esmeralda, considerada \"manteca\" por su textura dina al paladar."),
]

# (nombre, slug, municipio_slug, direccion, lat, lon, telefono, web, horario, activo, productos[])
COMERCIOS = [
    (
        "La Tienda Asturiana",
        "la-tienda-asturiana-gijon",
        "gijon",
        "Calle Corrida, 12, Gijón", 43.5453, -5.6615,
        "985 000 000", "https://ejemplo.com",
        "Lun-Sáb 10:00-20:00",
        False,
        ["sidra-natural"],
    ),
    (
        "Sr Lúpulo Despacho de Cervezas",
        "sr-lupulo-despacho-de-cervezas",
        "gijon",
        "Calle San Antonio, 5", 43.5453, -5.6615,
        None, None,
        "Lunes a jueves de 12:00 a 14:30h de 17:00 a 22:30h \nViernes y sábados de 12:00 a 14:30h de 17:00 a 23:30h",
        True,
        ["cerveza-artesana"],
    ),
    (
        "Al Peso Bar",
        "al-peso-bar",
        "gijon",
        "Calle Sta. Doradía, 19", 43.5453, -5.6615,
        None, None,
        "Lunes a sábado de 8:00 a 1:00h \nDomingos de 12:00 a 1:00h",
        True,
        ["queso-cabrales"],
    ),
    (
        "La Marina",
        "la-marina",
        "gijon",
        "Calle Martínez Marina, 6", 43.5453, -5.6615,
        "984 39 96 00", None,
        "Lunes - Viernes: 9:00-14:00 / 17:45-20:00\nSábado: 9:30 - 14:30",
        True,
        ["queso-afuega-l-pitu", "queso-cabrales", "faba-asturiana"],
    ),
    (
        "Somiedo Productos Asturianos",
        "somiedo-productos-asturianos",
        "gijon",
        "Calle San Bernardo, 4", 43.5453, -5.6615,
        "684 60 02 38", None,
        "Lunes - Viernes: 10:30 - 14:30 / 17:00 - 20:30\nSábado: 10:30 - 14:30\nDomingo: 10:30 - 15:00",
        True,
        ["queso-afuega-l-pitu", "queso-cabrales", "chorizo-asturiano", "sidra-natural", "faba-asturiana", "cerveza-artesana"],
    ),
    (
        "La Choricería",
        "la-chorícería",
        "gijon",
        "Calle Juan Alvargonzález, 42", 43.5453, -5.6615,
        None, None,
        "Lunes - Sábado: 10:00 - 14:00",
        True,
        ["queso-afuega-l-pitu", "queso-cabrales", "chorizo-asturiano", "morcilla-asturiana", "sidra-natural", "faba-asturiana", "queso-tres-leches-de-pria", "queso-la-peral"],
    ),
    (
        "La Esquina de Gijón",
        "la-esquina-de-gijon",
        "gijon",
        "Calle Magnus Blikstad, 28", 43.5453, -5.6615,
        None, None,
        "Lunes - Viernes: 9:30 - 14:00 / 18:00 - 20:00\nSábado: 9:30 - 14:00",
        True,
        ["queso-afuega-l-pitu", "queso-cabrales", "chorizo-asturiano", "morcilla-asturiana", "sidra-natural", "faba-asturiana", "queso-vidiago", "queso-tres-leches-de-pria", "queso-casin", "queso-la-peral"],
    ),
    (
        "Casa Marila",
        "casa-marila",
        "gijon",
        "Calle Rio Muni, 4", 43.5453, -5.6615,
        None, None,
        None,
        True,
        ["queso-cabrales", "chorizo-asturiano", "morcilla-asturiana", "casadielles", "faba-asturiana"],
    ),
    (
        "La Quesería",
        "la-queseria",
        "gijon",
        "Calle Aguado, 32", 43.5453, -5.6615,
        "985 37 28 40", None,
        None,
        True,
        ["queso-afuega-l-pitu", "queso-cabrales", "cerveza-artesana", "queso-vidiago", "queso-tres-leches-de-pria", "queso-casin", "queso-la-peral"],
    ),
    (
        "Comestibles la Gijonesa",
        "comestibles-la-gijonesa",
        "gijon",
        "Calle Covadonga, 24, Gijón", 43.5453, -5.6615,
        None, None,
        "Lunes - Sábado: 11:00 - 20:30\nDomingo: 11:30 - 15:00",
        True,
        ["queso-afuega-l-pitu", "queso-cabrales", "conservas-de-bonito", "casadielles", "sidra-natural", "cerveza-artesana", "queso-tres-leches-de-pria", "queso-casin", "queso-la-peral", "maranueles"],
    ),
    (
        "Quesería Cabrales 106",
        "queseria-cabrales-106",
        "gijon",
        "Calle Cabrales, 106, Gijón", 43.5453, -5.6615,
        None, None,
        "Lunes - Viernes: 10:00 - 14:00 / 17:30 - 20:30\nSábado: 10:30 - 14:30",
        True,
        ["queso-afuega-l-pitu", "queso-cabrales", "chorizo-asturiano", "morcilla-asturiana", "faba-asturiana", "queso-vidiago", "queso-tres-leches-de-pria", "queso-casin", "queso-la-peral"],
    ),
    (
        "Llagar Castañón",
        "llagar-castanon",
        "villaviciosa",
        "Carretera de San Miguel, 90-103, Quintueles(Villaviciosa)", 43.4833, -5.4333,
        None, "https://sidracastanon.com/",
        "Según horario visitas guiadas.",
        True,
        ["sidra-natural", "madera-tallada", "ceramica"],
    ),
    (
        "Llagar Herminio",
        "llagar-herminio",
        "siero",
        "Camino Real, 11, Colloto", 43.3893, -5.6598,
        None, None,
        None,
        True,
        ["sidra-natural"],
    ),
    (
        "Sidra Cortina",
        "sidra-cortina",
        "villaviciosa",
        "San Juan, 44, Amandi, Villaviciosa", 43.4833, -5.4333,
        None, None,
        None,
        True,
        ["sidra-natural"],
    ),
    (
        "Sidra Menendez",
        "sidra-menendez",
        "gijon",
        "Carretera AS-337, Fano, Gijón", 43.5453, -5.6615,
        "985 137 196", "https://www.sidramenendez.com/",
        "Lunes - Viernes: 9:00 - 14:00 / 16:00 - 19:30",
        True,
        ["sidra-natural"],
    ),
    (
        "Sidra trabanco",
        "sidra-trabanco",
        "gijon",
        "Carretera de Lavandera, 3255, Gijón", 43.5453, -5.6615,
        "985 136 462", "https://www.sidratrabanco.com/",
        "Lunes - Miércoles: 12:00 - 18:00\nJueves - Sábado: 12:00 - 1:00\nDomingo: 12:00 - 18:00",
        True,
        ["sidra-natural"],
    ),
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
        else:
            print("⏭ Categorías ya existen")

        # Productos
        if db.query(Producto).count() == 0:
            cats = {c.slug: c for c in db.query(Categoria).all()}
            for nombre, slug, cat_slug, desc in PRODUCTOS:
                db.add(Producto(
                    nombre=nombre,
                    slug=slug,
                    descripcion=desc,
                    categoria_id=cats[cat_slug].id,
                ))
            db.commit()
            print(f"✅ {len(PRODUCTOS)} productos insertados")
        else:
            print("⏭ Productos ya existen")

        # Comercios
        if db.query(Comercio).count() == 0:
            municipios = {m.slug: m for m in db.query(Municipio).all()}
            productos = {p.slug: p for p in db.query(Producto).all()}

            for nombre, slug, mun_slug, dir_, lat, lon, tel, web, horario, activo, prod_slugs in COMERCIOS:
                prods = [productos[s] for s in prod_slugs if s in productos]
                c = Comercio(
                    nombre=nombre,
                    slug=slug,
                    direccion=dir_,
                    lat=lat,
                    lon=lon,
                    telefono=tel,
                    web=web,
                    horario=horario,
                    municipio_id=municipios[mun_slug].id,
                    activo=activo,
                    api_key=secrets.token_hex(32),
                    productos=prods,
                )
                db.add(c)
            db.commit()
            print(f"✅ {len(COMERCIOS)} comercios insertados ({sum(1 for c in COMERCIOS if c[9])} activos)")
        else:
            print("⏭ Comercios ya existen")

        print("\n🎉 Seed completado")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
