import secrets
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from slugify import slugify

from app.core.database import get_db
from app.core.config import settings
from app.models.models import Municipio, Categoria, Producto, Comercio

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")

COOKIE_NAME = "admin_session"
COOKIE_MAX_AGE = 60 * 60 * 8  # 8 horas


def _signer():
    return URLSafeTimedSerializer(settings.SECRET_KEY, salt="admin-session")


def _crear_cookie(username: str) -> str:
    return _signer().dumps(username)


def _verificar_cookie(token: str) -> str | None:
    try:
        return _signer().loads(token, max_age=COOKIE_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


def _prefix(request: Request) -> str:
    return request.app.root_path


def verificar_admin(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=302, headers={"Location": _prefix(request) + "/admin/login"})
    user = _verificar_cookie(token)
    if not user:
        raise HTTPException(status_code=302, headers={"Location": _prefix(request) + "/admin/login"})
    return user


# ── Login / Logout ─────────────────────────────────────────
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if token and _verificar_cookie(token):
        return RedirectResponse(_prefix(request) + "/admin/", status_code=302)
    return templates.TemplateResponse("admin/login.html", {
        "request": request, "prefix": _prefix(request), "error": None
    })


@router.post("/login")
async def login_post(request: Request, response: Response):
    form = await request.form()
    username = form.get("username", "").strip()
    password = form.get("password", "")

    ok_user = secrets.compare_digest(username, settings.ADMIN_USERNAME)
    ok_pass = secrets.compare_digest(password, settings.ADMIN_PASSWORD)

    if not (ok_user and ok_pass):
        return templates.TemplateResponse("admin/login.html", {
            "request": request,
            "prefix": _prefix(request),
            "error": "Usuario o contraseña incorrectos"
        }, status_code=401)

    token = _crear_cookie(username)
    resp = RedirectResponse(_prefix(request) + "/admin/", status_code=303)
    resp.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    return resp


@router.get("/logout")
def logout(request: Request):
    resp = RedirectResponse(_prefix(request) + "/admin/login", status_code=302)
    resp.delete_cookie(COOKIE_NAME)
    return resp


# ── Dashboard ──────────────────────────────────────────────
@router.get("/", response_class=HTMLResponse)
def panel_admin(request: Request, db: Session = Depends(get_db), user: str = Depends(verificar_admin)):
    stats = {
        "municipios": db.query(Municipio).count(),
        "categorias": db.query(Categoria).count(),
        "productos": db.query(Producto).count(),
        "comercios_total": db.query(Comercio).count(),
        "comercios_activos": db.query(Comercio).filter(Comercio.activo == True).count(),
    }
    return templates.TemplateResponse("admin/index.html", {
        "request": request, "prefix": _prefix(request), "active": "inicio", "stats": stats
    })


# ── COMERCIOS ──────────────────────────────────────────────
@router.get("/comercios", response_class=HTMLResponse)
def listar_comercios(request: Request, db: Session = Depends(get_db), user: str = Depends(verificar_admin)):
    comercios = (
        db.query(Comercio)
        .options(joinedload(Comercio.municipio), joinedload(Comercio.productos))
        .order_by(Comercio.nombre)
        .all()
    )
    return templates.TemplateResponse("admin/comercios_lista.html", {
        "request": request, "prefix": _prefix(request), "active": "comercios", "comercios": comercios
    })


@router.get("/comercios/nuevo", response_class=HTMLResponse)
def form_nuevo_comercio(request: Request, db: Session = Depends(get_db), user: str = Depends(verificar_admin)):
    return templates.TemplateResponse("admin/comercio_form.html", {
        "request": request,
        "prefix": _prefix(request),
        "active": "comercios",
        "comercio": None,
        "municipios": db.query(Municipio).order_by(Municipio.nombre).all(),
        "productos": db.query(Producto).options(joinedload(Producto.categoria)).order_by(Producto.nombre).all(),
    })


@router.post("/comercios/nuevo")
async def crear_comercio(request: Request, db: Session = Depends(get_db), user: str = Depends(verificar_admin)):
    form = await request.form()
    nombre = form.get("nombre", "").strip()
    if not nombre:
        raise HTTPException(400, "El nombre es obligatorio")

    c = Comercio(
        nombre=nombre,
        slug=_slug_unico(nombre, Comercio, db),
        descripcion=form.get("descripcion") or None,
        direccion=form.get("direccion") or None,
        lat=_float(form.get("lat")),
        lon=_float(form.get("lon")),
        telefono=form.get("telefono") or None,
        web=form.get("web") or None,
        horario=form.get("horario") or None,
        municipio_id=int(form.get("municipio_id")),
        activo=bool(form.get("activo")),
        suscripcion_hasta=_parse_fecha(form.get("suscripcion_hasta", "")),
        api_key=secrets.token_hex(32),
        productos=_productos_seleccionados(form, db),
    )
    db.add(c)
    db.commit()
    return RedirectResponse(_prefix(request) + "/admin/comercios", status_code=303)


@router.get("/comercios/{id}/editar", response_class=HTMLResponse)
def form_editar_comercio(id: int, request: Request, db: Session = Depends(get_db), user: str = Depends(verificar_admin)):
    c = db.query(Comercio).options(joinedload(Comercio.productos)).filter(Comercio.id == id).first()
    if not c:
        raise HTTPException(404)
    return templates.TemplateResponse("admin/comercio_form.html", {
        "request": request,
        "prefix": _prefix(request),
        "active": "comercios",
        "comercio": c,
        "municipios": db.query(Municipio).order_by(Municipio.nombre).all(),
        "productos": db.query(Producto).options(joinedload(Producto.categoria)).order_by(Producto.nombre).all(),
    })


@router.post("/comercios/{id}/editar")
async def editar_comercio(id: int, request: Request, db: Session = Depends(get_db), user: str = Depends(verificar_admin)):
    c = db.query(Comercio).filter(Comercio.id == id).first()
    if not c:
        raise HTTPException(404)

    form = await request.form()
    c.nombre = form.get("nombre", c.nombre).strip()
    c.descripcion = form.get("descripcion") or None
    c.direccion = form.get("direccion") or None
    c.lat = _float(form.get("lat"))
    c.lon = _float(form.get("lon"))
    c.telefono = form.get("telefono") or None
    c.web = form.get("web") or None
    c.horario = form.get("horario") or None
    c.municipio_id = int(form.get("municipio_id"))
    c.activo = bool(form.get("activo"))
    c.suscripcion_hasta = _parse_fecha(form.get("suscripcion_hasta", ""))
    c.productos = _productos_seleccionados(form, db)
    db.commit()
    return RedirectResponse(_prefix(request) + "/admin/comercios", status_code=303)


@router.get("/comercios/{id}/toggle")
def toggle_comercio(id: int, request: Request, db: Session = Depends(get_db), user: str = Depends(verificar_admin)):
    c = db.query(Comercio).filter(Comercio.id == id).first()
    if not c:
        raise HTTPException(404)
    c.activo = not c.activo
    db.commit()
    return RedirectResponse(_prefix(request) + "/admin/comercios", status_code=303)


# ── CATEGORÍAS ─────────────────────────────────────────────
@router.get("/categorias", response_class=HTMLResponse)
def listar_categorias(request: Request, db: Session = Depends(get_db), user: str = Depends(verificar_admin)):
    cats = db.query(Categoria).options(joinedload(Categoria.productos)).order_by(Categoria.nombre).all()
    return templates.TemplateResponse("admin/categorias_lista.html", {
        "request": request, "prefix": _prefix(request), "active": "categorias", "categorias": cats
    })


@router.get("/categorias/nueva", response_class=HTMLResponse)
def form_nueva_categoria(request: Request, user: str = Depends(verificar_admin)):
    return templates.TemplateResponse("admin/categoria_form.html", {
        "request": request, "prefix": _prefix(request), "active": "categorias"
    })


@router.post("/categorias/nueva")
async def crear_categoria(request: Request, db: Session = Depends(get_db), user: str = Depends(verificar_admin)):
    form = await request.form()
    nombre = form.get("nombre", "").strip()
    db.add(Categoria(
        nombre=nombre,
        slug=slugify(nombre),
        descripcion=form.get("descripcion") or None,
        icono=form.get("icono") or None,
    ))
    db.commit()
    return RedirectResponse(_prefix(request) + "/admin/categorias", status_code=303)


# ── PRODUCTOS ──────────────────────────────────────────────
@router.get("/productos", response_class=HTMLResponse)
def listar_productos(request: Request, db: Session = Depends(get_db), user: str = Depends(verificar_admin)):
    prods = db.query(Producto).options(
        joinedload(Producto.categoria), joinedload(Producto.comercios)
    ).order_by(Producto.nombre).all()
    return templates.TemplateResponse("admin/productos_lista.html", {
        "request": request, "prefix": _prefix(request), "active": "productos", "productos": prods
    })


@router.get("/productos/nuevo", response_class=HTMLResponse)
def form_nuevo_producto(request: Request, db: Session = Depends(get_db), user: str = Depends(verificar_admin)):
    cats = db.query(Categoria).order_by(Categoria.nombre).all()
    return templates.TemplateResponse("admin/producto_form.html", {
        "request": request, "prefix": _prefix(request), "active": "productos", "categorias": cats
    })


@router.post("/productos/nuevo")
async def crear_producto(request: Request, db: Session = Depends(get_db), user: str = Depends(verificar_admin)):
    form = await request.form()
    nombre = form.get("nombre", "").strip()
    db.add(Producto(
        nombre=nombre,
        slug=slugify(nombre),
        descripcion=form.get("descripcion") or None,
        imagen_url=form.get("imagen_url") or None,
        categoria_id=int(form.get("categoria_id")),
    ))
    db.commit()
    return RedirectResponse(_prefix(request) + "/admin/productos", status_code=303)


# ── MUNICIPIOS ─────────────────────────────────────────────
@router.get("/municipios", response_class=HTMLResponse)
def listar_municipios(request: Request, db: Session = Depends(get_db), user: str = Depends(verificar_admin)):
    muns = db.query(Municipio).options(joinedload(Municipio.comercios)).order_by(Municipio.nombre).all()
    return templates.TemplateResponse("admin/municipios_lista.html", {
        "request": request, "prefix": _prefix(request), "active": "municipios", "municipios": muns
    })


# ── Helpers ────────────────────────────────────────────────
def _slug_unico(nombre: str, Model, db: Session) -> str:
    base = slugify(nombre)
    slug, i = base, 1
    while db.query(Model).filter(Model.slug == slug).first():
        slug = f"{base}-{i}"
        i += 1
    return slug


def _productos_seleccionados(form, db: Session) -> list:
    ids = form.getlist("producto_ids")
    return db.query(Producto).filter(Producto.id.in_(ids)).all() if ids else []


def _float(val) -> float | None:
    try:
        return float(val) if val else None
    except (ValueError, TypeError):
        return None


def _parse_fecha(val: str) -> datetime | None:
    try:
        return datetime.strptime(val, "%Y-%m-%d") if val else None
    except ValueError:
        return None
