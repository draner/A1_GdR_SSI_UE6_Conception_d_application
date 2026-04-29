# Endpoints de l'API pour le dashboard
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from si_barrage.templates import get_navbar

from ...db import get_db
from ..meteo import services as meteo_services
from . import services

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard_page():
    """
    Page principale du dashboard météo avec HTMX.
    """
    navbar = get_navbar(current_page="/meteo")

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Météo - SI Barrage</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <link rel="stylesheet" href="/assets/css/dashboards.css" />
    <style>
        /* Styles du menu de navigation */
        .navbar {{
            background-color: var(--bg-top);
            color: white;
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}

        .navbar-brand {{
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--accent);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .navbar-menu {{
            list-style: none;
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
        }}

        .navbar-link {{
            color: rgba(255, 255, 255, 0.8);
            text-decoration: none;
            padding: 8px 12px;
            border-radius: 4px;
            transition: all 0.3s ease;
        }}

        .navbar-link:hover {{
            color: white;
            background-color: rgba(255, 255, 255, 0.1);
        }}

        .navbar-link.active {{
            color: var(--accent);
            font-weight: 600;
            background-color: rgba(245, 158, 11, 0.1);
        }}
    </style>
</head>
<body class="dashboard-page">
    {navbar}
    <main class="dashboard-shell">
        <header class="dashboard-hero">
            <div>
                <div class="section-title">🌦️ Météo</div>
                <h1 class="dashboard-title">Dashboard météo</h1>
                <p class="dashboard-subtitle">Débits, pluies et prévisions consolidés dans une vue unique et lisible.</p>
            </div>
        </header>
        
        <!-- Première ligne : 3 colonnes -->
        <div class="top-row">
            <!-- Débit en temps réel -->
            <div class="metric-card">
                <div class="metric-title">Débit en temps réel</div>
                <div id="debit-reel" 
                     hx-get="/meteo/api/debit-reel" 
                     hx-trigger="load, every 10s"
                     hx-swap="innerHTML">
                    <div class="loading">
                        <div class="spinner" style="width: 16px; height: 16px; border-width: 2px;"></div>
                    </div>
                </div>
            </div>

            <!-- Historique des débits -->
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">📋</span>
                    <h2 class="card-title">Historique des débits</h2>
                </div>
                <div id="historique-debits" 
                     hx-get="/meteo/api/historique-debits" 
                     hx-trigger="load, every 10s"
                     hx-swap="innerHTML">
                    <div class="loading">
                        <div class="spinner" style="width: 16px; height: 16px; border-width: 2px;"></div>
                    </div>
                </div>
            </div>

            <!-- Graphique des débits + prévisions -->
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">📊</span>
                    <h2 class="card-title">Graphique débits et prévisions</h2>
                </div>
                <div id="graphique-debits" 
                     hx-get="/meteo/api/debit-graph" 
                     hx-trigger="load, every 10s"
                     hx-swap="innerHTML">
                    <div class="loading">
                        <div class="spinner"></div>
                        Chargement...
                    </div>
                </div>
            </div>
        </div>

        <!-- Deuxième ligne : 4 colonnes (2 colonnes x 2) -->
        <div class="bottom-row">
            <!-- Historique des pluies -->
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">💧</span>
                    <h2 class="card-title">Historique pluies</h2>
                </div>
                <div id="historique-pluie" 
                     hx-get="/meteo/api/historique-pluie" 
                     hx-trigger="load, every 10s"
                     hx-swap="innerHTML">
                    <div class="loading">
                        <div class="spinner" style="width: 16px; height: 16px; border-width: 2px;"></div>
                    </div>
                </div>
            </div>

            <!-- Graphique pluie + prévision -->
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">🌧️</span>
                    <h2 class="card-title">Graphique pluie et prévision</h2>
                </div>
                <div id="graphique-pluie" 
                     hx-get="/meteo/api/pluie-graph" 
                     hx-trigger="load, every 10s"
                     hx-swap="innerHTML">
                    <div class="loading">
                        <div class="spinner"></div>
                        Chargement...
                    </div>
                </div>
            </div>

            <!-- Estimation crue rivière -->
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">⚠️</span>
                    <h2 class="card-title">Estimation crue rivière</h2>
                </div>
                <div id="estimation-crue" 
                     hx-get="/meteo/api/estimation-crue" 
                     hx-trigger="load, every 10s"
                     hx-swap="innerHTML">
                    <div class="loading">
                        <div class="spinner" style="width: 16px; height: 16px; border-width: 2px;"></div>
                    </div>
                </div>
            </div>

            <!-- Conseil gestion opération -->
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">💡</span>
                    <h2 class="card-title">Conseil gestion opération</h2>
                </div>
                <div id="conseils-operation" 
                     hx-get="/meteo/api/conseils-operation" 
                     hx-trigger="load, every 10s"
                     hx-swap="innerHTML">
                    <div class="loading">
                        <div class="spinner" style="width: 16px; height: 16px; border-width: 2px;"></div>
                    </div>
                </div>
            </div>
        </div>
    </main>
</body>
</html>
    """
    return HTMLResponse(content=html_content)
