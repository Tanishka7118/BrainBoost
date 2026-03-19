from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["pages"])


@router.get("/")
def home():
    return RedirectResponse(url="/login", status_code=302)


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"title": "Login"})


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {"title": "Register"})


@router.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {"title": "Dashboard"})


@router.get("/revision")
def revision_page(request: Request):
    return templates.TemplateResponse(request, "revision.html", {"title": "Revision"})
