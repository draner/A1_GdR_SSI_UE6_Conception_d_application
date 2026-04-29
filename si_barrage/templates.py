"""
Templates HTML réutilisables pour l'application SI Barrage.
"""


def get_navbar(current_page: str = "") -> str:
    """
    Génère le menu de navigation commun.

    Args:
        current_page: Le chemin de la page actuelle pour mettre en surbrillance le lien actif
    """
    menu_items = [
        ("Accueil", "/"),
        ("Maintenance", "/maintenance/home"),
        ("Tickets", "/maintenance/tickets"),
        ("Interventions", "/maintenance/interventions"),
        ("Production", "/production"),
        ("Météo", "/meteo"),
    ]

    nav_html = '<nav class="navbar">'
    nav_html += '<a href="/" class="navbar-brand">🏗️ SI Barrage</a>'
    nav_html += '<ul class="navbar-menu">'

    for label, link in menu_items:
        if link == "/":
            is_active = current_page == "/"
        else:
            is_active = bool(current_page and current_page.startswith(link))
        active_class = "active" if is_active else ""
        nav_html += (
            f'<li><a href="{link}" class="navbar-link {active_class}">{label}</a></li>'
        )

    nav_html += "</ul></nav>"
    return nav_html


def get_page_template(title: str, content: str, current_page: str = "") -> str:
    """
    Génère un template HTML complet avec navbar, styles et contenu.

    Args:
        title: Titre de la page
        content: Contenu HTML à afficher
        current_page: Chemin de la page actuelle pour le menu
    """
    navbar = get_navbar(current_page)

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - SI Barrage</title>
    <link rel="stylesheet" href="/assets/css/dashboards.css">
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

        /* Conteneur principal */
        .main-container {{
            max-width: 1440px;
            margin: 0 auto;
        }}

        /* Styles pour les cartes de dashboard */
        .dashboard-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            margin-top: 32px;
        }}

        .dashboard-card {{
            background-color: var(--surface-strong);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            text-decoration: none;
            color: inherit;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        }}

        .dashboard-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.15);
            border-color: var(--primary);
        }}

        .dashboard-card-icon {{
            font-size: 2.5rem;
            margin-bottom: 12px;
        }}

        .dashboard-card-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--text);
        }}

        .dashboard-card-description {{
            color: var(--muted);
            font-size: 0.95rem;
            line-height: 1.5;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .navbar {{
                flex-direction: column;
                gap: 16px;
            }}

            .navbar-menu {{
                justify-content: center;
            }}

            body {{
                padding: 12px;
            }}
        }}
    </style>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
</head>
<body class="dashboard-page">
    {navbar}
    <div class="main-container dashboard-shell">
        {content}
    </div>
</body>
</html>
"""
    return html
