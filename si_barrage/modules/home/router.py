# Routeur pour la page d'accueil
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from si_barrage.templates import get_page_template

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home_page():
    """
    Page d'accueil avec liste des dashboards disponibles.
    """
    content = """
    <div class="dashboard-hero">
        <div>
            <h1 class="section-title">Système d'Information Barrage</h1>
            <p style="color: var(--muted); margin-top: 12px; max-width: 600px;">
                Bienvenue sur la plateforme de gestion du barrage. Accédez aux différents 
                tableaux de bord pour suivre la production, la maintenance et les conditions météorologiques.
            </p>
        </div>
    </div>

    <div class="dashboard-cards">
        <a href="/maintenance" class="dashboard-card">
            <div class="dashboard-card-icon">🔧</div>
            <div class="dashboard-card-title">Maintenance</div>
            <div class="dashboard-card-description">
                Gestion des tickets de maintenance et suivi des équipements.
            </div>
        </a>

        <a href="/maintenance/interventions" class="dashboard-card">
            <div class="dashboard-card-icon">👨‍🔧</div>
            <div class="dashboard-card-title">Interventions</div>
            <div class="dashboard-card-description">
                Historique et détails des interventions techniques réalisées.
            </div>
        </a>

        <a href="/production" class="dashboard-card">
            <div class="dashboard-card-icon">⚡</div>
            <div class="dashboard-card-title">Production</div>
            <div class="dashboard-card-description">
                Suivi de la production d'électricité et des volumes d'eau.
            </div>
        </a>

        <a href="/meteo" class="dashboard-card">
            <div class="dashboard-card-icon">🌤️</div>
            <div class="dashboard-card-title">Météo</div>
            <div class="dashboard-card-description">
                Conditions météorologiques actuelles et prévisions.
            </div>
        </a>
    </div>
    """

    return get_page_template("Accueil", content, current_page="/")
