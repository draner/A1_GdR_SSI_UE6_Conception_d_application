# Endpoints de l'API pour le dashboard
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from si_barrage.templates import get_page_template

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard_page():
    """
    Page principale du dashboard avec HTMX.
    """
    content = """
    <div class="dashboard-hero">
        <div>
            <h1 class="section-title">Dashboard</h1>
            <p style="color: var(--muted); margin-top: 12px;">
                Vue d'ensemble des informations principales du barrage.
            </p>
        </div>
    </div>

    <div style="background-color: var(--surface-strong); padding: 24px; border-radius: 12px; border: 1px solid var(--border);">
        <p style="color: var(--muted); text-align: center;">
            Contenu du dashboard à venir...
        </p>
    </div>
    """

    return get_page_template("Dashboard", content, current_page="/dashboard")
