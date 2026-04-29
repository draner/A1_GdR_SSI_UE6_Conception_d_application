from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Path, Query
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from si_barrage.db import get_db
from si_barrage.templates import get_navbar, get_page_template

from . import services
from .models import MaintenanceTicket
from .schemas import AnalyseRead, InterventionCreate, InterventionRead
from .ui_router import router as ui_router

router = APIRouter()

# Sous-routeurs
router.include_router(ui_router, prefix="", tags=["UI Maintenance"])


@router.get("/", response_class=HTMLResponse)
async def maintenance_home():
    """
    Page d'accueil du module maintenance avec liens vers les actions principales.
    """
    content = """
    <div class="dashboard-hero">
        <div>
            <h1 class="section-title">🔧 Maintenance</h1>
            <p style="color: var(--muted); margin-top: 12px; max-width: 600px;">
                Gestion de la maintenance du barrage. Créez des tickets, consultez l'historique 
                des interventions et suivez les équipements.
            </p>
        </div>
    </div>

    <div class="dashboard-cards">
        <a href="/maintenance/nouveau-ticket" class="dashboard-card">
            <div class="dashboard-card-icon">➕</div>
            <div class="dashboard-card-title">Nouveau Ticket</div>
            <div class="dashboard-card-description">
                Créer un nouveau ticket de maintenance pour signaler un problème.
            </div>
        </a>

        <a href="/maintenance/interventions" class="dashboard-card">
            <div class="dashboard-card-icon">📋</div>
            <div class="dashboard-card-title">Historique Interventions</div>
            <div class="dashboard-card-description">
                Consulter l'historique et les détails des interventions par équipement.
            </div>
        </a>

        <a href="/maintenance/tickets" class="dashboard-card">
            <div class="dashboard-card-icon">📝</div>
            <div class="dashboard-card-title">Tous les Tickets</div>
            <div class="dashboard-card-description">
                Liste de tous les tickets de maintenance créés.
            </div>
        </a>
    </div>
    """

    return get_page_template("Maintenance", content, current_page="/maintenance")


@router.post("/tickets")
async def create_ticket(
    nom: str = Form(...),
    id_equipement: str = Form(...),
    nom_equipement: str = Form(...),
    statut: str = Form(...),
    description: str = Form(...),
    date_creation: str = Form(...),
    niv_urgence: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Création d'un ticket de maintenance.

    Logique retenue :
    - on crée une nouvelle ligne dans la table `maintenance`
    - `description` contient uniquement le problème
    - `intervenant` contient le nom du technicien
    - `solution` stocke temporairement le niveau d'urgence
    - après insertion, on recopie l'identifiant auto-généré `id`
      dans `ticket_id` pour que les nouveaux tickets aient eux aussi
      un numéro de ticket visible dans le TDB
    """
    try:
        new_ticket = MaintenanceTicket(
            id_equipement=id_equipement.strip(),
            nom_equipement=nom_equipement.strip(),
            statut=statut.strip(),
            description=description.strip(),
            date_creation=date_creation,
            intervenant=nom.strip(),
            solution=f"Niveau d'urgence: {niv_urgence.strip()}",
        )

        # Étape 1 : insertion
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)

        # Étape 2 : on affecte ticket_id = id
        # Cela permet d'avoir un vrai numéro de ticket
        # même pour les nouvelles lignes créées via le formulaire.
        new_ticket.ticket_id = new_ticket.id
        db.commit()

        return RedirectResponse(url="/maintenance/", status_code=303)

    except Exception as e:
        db.rollback()
        print("Erreur création ticket:", e)
        return RedirectResponse(
            url="/maintenance/nouveau-ticket?error=1",
            status_code=303,
        )


@router.get("/nouveau-ticket", response_class=HTMLResponse)
async def nouveau_ticket_page():
    """
    Formulaire HTML de création d'un nouveau ticket.
    """
    navbar = get_navbar(current_page="/maintenance")

    navbar_styles = """
    <style>
        /* Styles du menu de navigation */
        .navbar {
            background-color: var(--bg-top);
            color: white;
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .navbar-brand {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--accent);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .navbar-menu {
            list-style: none;
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
        }

        .navbar-link {
            color: rgba(255, 255, 255, 0.8);
            text-decoration: none;
            padding: 8px 12px;
            border-radius: 4px;
            transition: all 0.3s ease;
        }

        .navbar-link:hover {
            color: white;
            background-color: rgba(255, 255, 255, 0.1);
        }

        .navbar-link.active {
            color: var(--accent);
            font-weight: 600;
            background-color: rgba(245, 158, 11, 0.1);
        }
    </style>
    """

    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nouveau ticket — Maintenance</title>
        <link rel="stylesheet" href="/assets/css/dashboards.css" />
        {navbar_styles}
    </head>
    <body class="form-page">
      {navbar}
      <main class="dashboard-shell form-shell">
        <a href="/maintenance/" class="back-link">← Retour au tableau de bord</a>

        <div class="form-card">
          <h1>➕ Nouveau ticket de maintenance</h1>

          <form action="/maintenance/tickets" method="POST">
            <div class="form-group">
                <label for="nom">Technicien :</label>
                <input type="text" id="nom" name="nom" required>
            </div>

            <div class="form-group">
                <label for="id_equipement">ID Équipement :</label>
                <input type="text" id="id_equipement" name="id_equipement" required>
            </div>

            <div class="form-group">
                <label for="nom_equipement">Nom Équipement :</label>
                <input type="text" id="nom_equipement" name="nom_equipement" required>
            </div>

            <div class="form-group">
                <label for="statut">Statut :</label>
                <select id="statut" name="statut" required>
                    <option value="">Choisir...</option>
                    <option value="En cours">En cours</option>
                    <option value="En attente">En attente</option>
                    <option value="Terminé">Terminé</option>
                </select>
            </div>

            <div class="form-group">
                <label for="niv_urgence">Niveau d'urgence :</label>
                <select id="niv_urgence" name="niv_urgence" required>
                    <option value="">Choisir...</option>
                    <option value="faible">Faible</option>
                    <option value="moyen">Moyen</option>
                    <option value="urgent">Urgent</option>
                    <option value="critique">Critique</option>
                </select>
            </div>

            <div class="form-group">
                <label for="description">Description du problème :</label>
                <textarea id="description" name="description" rows="4" required
                          placeholder="Décrivez précisément le problème rencontré..."></textarea>
            </div>

            <div class="form-group">
                <label>Date de création :</label>
                <input type="date" id="date_creation" name="date_creation" required>
            </div>

            <button type="submit" class="btn">Créer le ticket</button>
                    </form>
                </div>
            </main>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/tickets")
def list_tickets(db: Session = Depends(get_db)):
    """
    Liste brute des tickets encore actifs.

    On exclut les lignes marquées 'Supprimé'.
    """
    tickets = (
        db.query(MaintenanceTicket)
        .filter(MaintenanceTicket.statut != "Supprimé")
        .order_by(MaintenanceTicket.id.desc())
        .all()
    )

    return [
        {
            "id": t.id,
            "ticket_id": t.ticket_id,
            "id_equipement": t.id_equipement,
            "nom_equipement": t.nom_equipement,
            "statut": t.statut,
            "description": t.description,
            "date_creation": t.date_creation,
            "intervenant": t.intervenant,
        }
        for t in tickets
    ]


@router.get(
    "/equipements/{id_equipement}/interventions",
    response_model=List[InterventionRead],
    summary="Lister l'historique d'interventions d'un équipement",
)
def get_interventions(
    id_equipement: str = Path(..., examples=["T1"]),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Retourne l'historique des interventions d'un équipement.
    """
    if not services.equipment_exists(db, id_equipement):
        raise HTTPException(
            status_code=404,
            detail=f"Équipement inconnu: {id_equipement}",
        )

    interventions = services.get_interventions(
        db,
        id_equipement,
        limit=limit,
        offset=offset,
    )
    return interventions


@router.get(
    "/interventions/{intervention_id}",
    response_model=InterventionRead,
    summary="Détail d'une intervention",
)
def get_intervention_detail(
    intervention_id: int,
    db: Session = Depends(get_db),
):
    """
    Retourne le détail d'une intervention.
    """
    intervention = services.get_intervention_by_id(db, intervention_id)
    if not intervention:
        raise HTTPException(
            status_code=404,
            detail=f"Intervention introuvable: {intervention_id}",
        )
    return intervention


@router.post(
    "/equipements/{id_equipement}/interventions",
    response_model=InterventionRead,
    status_code=201,
    summary="Créer une intervention pour un équipement",
)
def create_intervention(
    payload: InterventionCreate,
    id_equipement: str = Path(..., examples=["T1"]),
    db: Session = Depends(get_db),
):
    """
    Crée une intervention métier pour un équipement donné.
    """
    if not services.equipment_exists(db, id_equipement):
        raise HTTPException(
            status_code=404,
            detail=f"Équipement inconnu: {id_equipement}",
        )

    if payload.ticket_id is not None:
        ticket = (
            db.query(MaintenanceTicket)
            .filter(MaintenanceTicket.id == payload.ticket_id)
            .first()
        )
        if not ticket:
            raise HTTPException(
                status_code=404,
                detail=f"Ticket introuvable: {payload.ticket_id}",
            )
        if ticket.id_equipement != id_equipement:
            raise HTTPException(
                status_code=400,
                detail="ticket_id ne correspond pas à l'équipement demandé",
            )

    created = services.create_intervention(db, id_equipement, payload)
    return created


@router.get(
    "/equipements/{id_equipement}/interventions/analyse",
    response_model=AnalyseRead,
    summary="Analyse des pannes récurrentes (top N problèmes)",
)
def analyse_interventions(
    id_equipement: str = Path(..., examples=["T1"]),
    top_n: int = Query(5, ge=1, le=50),
    start_date: Optional[str] = Query(
        None,
        description="Filtre date ISO YYYY-MM-DD (inclusive)",
    ),
    end_date: Optional[str] = Query(
        None,
        description="Filtre date ISO YYYY-MM-DD (inclusive)",
    ),
    db: Session = Depends(get_db),
):
    """
    Retourne l'analyse des pannes récurrentes d'un équipement.
    """
    if not services.equipment_exists(db, id_equipement):
        raise HTTPException(
            status_code=404,
            detail=f"Équipement inconnu: {id_equipement}",
        )

    for label, value in [("start_date", start_date), ("end_date", end_date)]:
        if value is not None:
            try:
                date.fromisoformat(value)
            except Exception:
                raise HTTPException(
                    status_code=422,
                    detail=f"{label} doit être au format ISO YYYY-MM-DD",
                )

    total, top, periode = services.analyse_recurrent_breakdowns(
        db,
        id_equipement,
        top_n=top_n,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "id_equipement": id_equipement,
        "total_interventions": total,
        "top_problemes": top,
        "periode": periode,
    }


@router.delete("/tickets/{ticket_id}")
async def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """
    Suppression logique d'un ticket.

    On ne supprime pas physiquement la ligne de la base.
    On la marque comme 'Supprimé' pour :
    - garder la traçabilité
    - masquer la ligne dans le TDB
    - exclure la ligne des KPI et de l'historique affiché

    Important :
    ici `ticket_id` correspond à l'identifiant réel de la ligne
    dans la table `maintenance`.
    """
    try:
        ticket = (
            db.query(MaintenanceTicket)
            .filter(MaintenanceTicket.id == ticket_id)
            .first()
        )

        if not ticket:
            return Response(
                status_code=404,
                content="Ticket introuvable.",
            )

        if ticket.statut == "Supprimé":
            return Response(
                status_code=200,
                content="Le ticket était déjà supprimé.",
            )

        ticket.statut = "Supprimé"
        db.commit()

        return Response(
            status_code=200,
            content=f"Suppression effectuée avec succès pour l'équipement {ticket.id_equipement}.",
        )

    except Exception as e:
        db.rollback()
        print("Erreur suppression:", e)
        return Response(
            status_code=500,
            content="Erreur lors de la suppression.",
        )


@router.get("/", response_class=HTMLResponse)
async def maintenance_dashboard_page():
    """
    Page principale du tableau de bord maintenance.

    Cette page charge dynamiquement :
    - les KPI
    - les filtres
    - le tableau des équipements

    Le style est volontairement harmonisé avec la page Historique
    pour donner une interface cohérente, premium et professionnelle.
    """
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Maintenance — Vue globale</title>
      <script src="https://unpkg.com/htmx.org@1.9.10"></script>
            <link rel="stylesheet" href="/assets/css/dashboards.css" />
    </head>
        <body class="dashboard-page">
            <main class="dashboard-shell dashboard-stack">
                <header class="dashboard-hero">
                    <div>
                        <div class="section-title">🛠️ Maintenance</div>
                        <h1 class="dashboard-title">Vue globale du parc</h1>
                        <p class="dashboard-subtitle">Vue synthétique du dernier état connu de chaque équipement.</p>
                    </div>
                </header>

                <div id="flash-message" class="flash-message"></div>

                <section class="card">
                    <div class="panel-title">Répartition des équipements par statut</div>
                    <div id="kpis"
                            hx-get="/maintenance/api/kpis"
                            hx-trigger="load, every 10s"
                            hx-swap="innerHTML">
                    </div>
                </section>

                <section class="card">
                    <div class="panel-title">Tableau récapitulatif des maintenances</div>
                    <div class="info-note">
                        Le tableau affiche au maximum les 5 dernières entrées visibles, après application des filtres.
                    </div>

                    <div id="filter"
                             hx-get="/maintenance/api/id-prefix-filter"
                             hx-trigger="load"
                             hx-swap="innerHTML">
                    </div>

                    <div id="equipment-table"
                             hx-get="/maintenance/api/equipment-table"
                             hx-trigger="load, every 10s"
                             hx-include="#prefix-select, #status-select"
                             hx-swap="innerHTML">
                        <div class="loading-box">Chargement…</div>
                    </div>
                </section>

                <div class="actions">
                    <a href="/maintenance/nouveau-ticket" class="btn-primary">
                        ➕ Créer un nouveau ticket
                    </a>

                    <a href="/maintenance/interventions" class="btn-secondary">
                        🛠️ Voir l'historique des interventions
                    </a>
                </div>

            </main>

      <script>
        document.body.addEventListener("htmx:afterRequest", function(event) {
          const elt = event.detail.elt;

          if (elt && elt.matches(".btn-delete") && event.detail.successful) {
            const equipmentName = elt.getAttribute("data-equipment-name") || "cet équipement";

            const flash = document.getElementById("flash-message");
            flash.textContent = "Suppression effectuée avec succès pour " + equipmentName + ".";
            flash.style.display = "block";

            htmx.ajax("GET", "/maintenance/api/equipment-table", {
              target: "#equipment-table",
              swap: "innerHTML",
              values: {
                prefix: document.getElementById("prefix-select")?.value || "",
                status: document.getElementById("status-select")?.value || ""
              }
            });

            htmx.ajax("GET", "/maintenance/api/kpis", {
              target: "#kpis",
              swap: "innerHTML"
            });

            setTimeout(() => {
              flash.style.display = "none";
            }, 3000);
          }
        });
      </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/api/equipment-table", response_class=HTMLResponse)
async def equipment_table(
    prefix: str = "",
    status: str = "",
    db: Session = Depends(get_db),
):
    """
    Construit le tableau du TDB.

    Important :
    - le TDB n'affiche qu'une seule ligne par équipement : la plus récente
    - le service limite déjà le résultat aux 5 dernières entrées visibles
    - la suppression utilise le vrai `id` de la ligne dans la table maintenance
    """
    rows = services.get_equipment_events(db, prefix, status)

    trs = ""
    for r in rows:
        row_class = ""

        if r["statut"] == "Terminé":
            row_class = "status-termine"
        elif r["statut"] == "En cours":
            row_class = "status-encours"
        elif r["statut"] == "En attente":
            row_class = "status-attente"

        equipment_name = r["nom_equipement"] or r["id_equipement"]

        delete_btn = f"""
        <button
          class="btn-delete"
          data-equipment-name="{equipment_name}"
          hx-delete="/maintenance/tickets/{r["id"]}"
          hx-confirm="Voulez-vous vraiment supprimer l’équipement {equipment_name} ?"
        >
          Supprimer
        </button>
        """

        trs += f"""
        <tr class="{row_class}">
          <td class="mono">{r["id_equipement"]}</td>
          <td>{r["nom_equipement"] or ""}</td>
          <td>{r["statut"] or ""}</td>
          <td>{r["date_creation"] or ""}</td>
          <td>{r["ticket_id"] if r["ticket_id"] is not None else ""}</td>
          <td>{r["description"] or ""}</td>
          <td>{delete_btn}</td>
        </tr>
        """

    html = f"""
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nom</th>
            <th>Dernier statut</th>
            <th>Dernière MAJ</th>
            <th>Num_ticket</th>
            <th>Description</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {trs if trs else '<tr><td colspan="7">Aucune donnée maintenance.</td></tr>'}
        </tbody>
      </table>
    </div>
    """
    return HTMLResponse(content=html)


@router.get("/api/kpis", response_class=HTMLResponse)
async def kpis(db: Session = Depends(get_db)):
    """
    Retourne les KPI du tableau de bord :
    - terminés
    - en cours
    - en attente
    """
    data = services.get_kpis(db)

    html = f"""
    <div class="kpi-grid">
        <div class="kpi-card kpi-termine">
            <div class="kpi-number">{data["termines"]}</div>
            <div class="kpi-label">Terminés</div>
        </div>

        <div class="kpi-card kpi-encours">
            <div class="kpi-number">{data["encours"]}</div>
            <div class="kpi-label">En cours</div>
        </div>

        <div class="kpi-card kpi-attente">
            <div class="kpi-number">{data["attente"]}</div>
            <div class="kpi-label">En attente</div>
        </div>
    </div>
    """
    return HTMLResponse(content=html)


@router.get("/api/id-prefix-filter", response_class=HTMLResponse)
async def id_prefix_filter(db: Session = Depends(get_db)):
    """
    Construit les filtres du TDB :
    - filtre par préfixe d'équipement
    - filtre par statut
    """
    prefixes = services.get_id_prefixes(db)

    options = '<option value="">Tous</option>'
    for p in prefixes:
        options += f'<option value="{p}">{p}</option>'

    html = f"""
    <div class="filter-bar">
        <div class="field">
            <label for="prefix-select">Filtre ID</label>
            <select id="prefix-select"
                    name="prefix"
                    hx-preserve="true"
                    hx-get="/maintenance/api/equipment-table"
                    hx-trigger="change"
                    hx-target="#equipment-table"
                    hx-include="#prefix-select, #status-select">
                {options}
            </select>
        </div>

        <div class="field">
            <label for="status-select">Filtre statut</label>
            <select id="status-select"
                    name="status"
                    hx-preserve="true"
                    hx-get="/maintenance/api/equipment-table"
                    hx-trigger="change"
                    hx-target="#equipment-table"
                    hx-include="#prefix-select, #status-select">
                <option value="">Tous</option>
                <option value="Terminé">Vert - Terminé</option>
                <option value="En cours">Orange - En cours</option>
                <option value="En attente">Rouge - En attente</option>
            </select>
        </div>
    </div>
    """

    return HTMLResponse(content=html)
