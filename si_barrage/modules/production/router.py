# Endpoints de l'API pour la production
from datetime import date
from typing import List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from ...db import get_db
from .models import MeteoHistoriqueModel, ProductionDataModel

router = APIRouter()


def _get_centrale_params(db: Session) -> Tuple[float, int, float]:
    row = db.execute(
        text(
            """
            SELECT prix_electricite_eur_mwh, nombre_turbines, puissance_nominale_mw
            FROM centrale_parametres
            ORDER BY id DESC
            LIMIT 1
            """
        )
    ).fetchone()

    if not row:
        raise ValueError(
            "Paramètres de centrale introuvables. Initialise la table centrale_parametres."
        )

    if row[0] is None or row[1] is None or row[2] is None:
        raise ValueError("Paramètres de centrale incomplets dans centrale_parametres.")

    prix = float(row[0])
    nb_turbines = int(row[1])
    puissance_nominale = float(row[2])
    return prix, nb_turbines, puissance_nominale


def _load_dashboard_data(db: Session) -> Tuple[pd.DataFrame, pd.DataFrame]:
    prix_electricite, nb_turbines, puissance_nominale = _get_centrale_params(db)

    production_rows = db.execute(
        text(
            """
            SELECT date, production_mwh, volume_eau_m3
            FROM production
            ORDER BY date ASC
            """
        )
    ).fetchall()

    meteo_rows = db.execute(
        text(
            """
            SELECT date, debit_riviere_m3s, pluviometrie_mm
            FROM meteo
            ORDER BY date ASC
            """
        )
    ).fetchall()

    prevision_rows = db.execute(
        text(
            """
            SELECT date_prevision, debit_riviere_m3s_prevu
            FROM meteo_previsions
            ORDER BY date_prevision ASC
            """
        )
    ).fetchall()

    production_data = pd.DataFrame(
        production_rows,
        columns=["date", "production_mwh", "volume_eau_m3"],
    )
    meteo_historique = pd.DataFrame(
        meteo_rows,
        columns=["date", "debit_riviere_m3s", "pluviometrie_mm"],
    )
    meteo_prevision = pd.DataFrame(
        prevision_rows,
        columns=["date_prevision", "debit_riviere_m3s_prevu"],
    )

    if not production_data.empty:
        production_data["date"] = pd.to_datetime(production_data["date"])
    if not meteo_historique.empty:
        meteo_historique["date"] = pd.to_datetime(meteo_historique["date"])

    df = production_data.merge(meteo_historique, on="date", how="inner")
    if not df.empty:
        df["efficacite"] = df["production_mwh"] / df["volume_eau_m3"].replace(0, pd.NA)
        efficacite_moyenne = float(df["efficacite"].mean(skipna=True) or 0)
        df["production_max"] = nb_turbines * puissance_nominale * 24
        df["taux_charge"] = (df["production_mwh"] / df["production_max"]) * 100
        df["revenu"] = df["production_mwh"] * prix_electricite
    else:
        efficacite_moyenne = 0.0
        df = pd.DataFrame(
            columns=[
                "date",
                "production_mwh",
                "volume_eau_m3",
                "debit_riviere_m3s",
                "pluviometrie_mm",
                "efficacite",
                "production_max",
                "taux_charge",
                "revenu",
            ]
        )

    if not meteo_prevision.empty:
        meteo_prevision["date_prevision"] = pd.to_datetime(
            meteo_prevision["date_prevision"]
        )
    meteo_prevision["volume_estime_m3"] = (
        meteo_prevision["debit_riviere_m3s_prevu"] * 86400
    )
    meteo_prevision["production_estimee_mwh"] = (
        meteo_prevision["volume_estime_m3"] * efficacite_moyenne
    )
    production_max = nb_turbines * puissance_nominale * 24
    meteo_prevision["production_estimee_mwh"] = meteo_prevision[
        "production_estimee_mwh"
    ].clip(upper=production_max)
    meteo_prevision["revenu_estime"] = (
        meteo_prevision["production_estimee_mwh"] * prix_electricite
    )

    return df, meteo_prevision


# --- API Models and Endpoints ---


@router.get("/", response_class=HTMLResponse)
async def root(
    db: Session = Depends(get_db),
    seuil_sous_prod: Optional[float] = None,
    seuil_sur_prod: Optional[float] = None,
):
    df, meteo_prevision = _load_dashboard_data(db)
    # Production chart
    fig_prod = go.Figure()
    fig_prod.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["production_mwh"],
            name="Production",
            line=dict(color="black"),
        )
    )
    fig_prod.update_layout(
        title="Production (MWh)", height=350, margin=dict(l=20, r=20, t=40, b=20)
    )
    prod_html = fig_prod.to_html(full_html=False, include_plotlyjs="cdn")

    # Rendement chart
    fig_rend = px.line(
        df, x="date", y="efficacite", title="Efficacité Hydraulique (MWh/m³)"
    )
    fig_rend.update_layout(height=350)
    rend_html = fig_rend.to_html(full_html=False, include_plotlyjs=False)

    # Revenu chart
    fig_rev = px.line(df, x="date", y="revenu", title="Revenu Journalier (€)")
    fig_rev.update_layout(height=320)
    rev_html = fig_rev.to_html(full_html=False, include_plotlyjs=False)

    # Taux de charge chart
    fig_taux = px.line(df, x="date", y="taux_charge", title="Taux de charge (%)")
    fig_taux.update_layout(height=320)
    taux_html = fig_taux.to_html(full_html=False, include_plotlyjs=False)

    # Simulation chart (prévision)
    fig_sim = go.Figure()
    fig_sim.add_trace(
        go.Bar(
            x=meteo_prevision["date_prevision"],
            y=meteo_prevision["production_estimee_mwh"],
            name="Production estimée (MWh)",
            marker_color="#2ca02c",
        )
    )
    fig_sim.add_trace(
        go.Bar(
            x=meteo_prevision["date_prevision"],
            y=meteo_prevision["revenu_estime"],
            name="Revenu estimé (€)",
            marker_color="#1f77b4",
        )
    )
    fig_sim.update_layout(
        barmode="group",
        title="Simulation de production et revenu",
        height=320,
        xaxis_title="Date prévision",
        yaxis_title="Valeur",
    )
    sim_html = fig_sim.to_html(full_html=False, include_plotlyjs=False)

    # Alertes chart (points sous/sur production)
    if df.empty:
        seuil_bas = 0.0
        seuil_haut = 0.0
    else:
        seuil_bas = (
            seuil_sous_prod
            if seuil_sous_prod is not None
            else float(df["production_mwh"].quantile(0.25))
        )
        seuil_haut = (
            seuil_sur_prod
            if seuil_sur_prod is not None
            else float(df["production_mwh"].quantile(0.75))
        )
    alert_low = df[df["production_mwh"] < seuil_bas]
    alert_high = df[df["production_mwh"] > seuil_haut]
    fig_alert = go.Figure()
    fig_alert.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["production_mwh"],
            name="Production",
            line=dict(color="black"),
        )
    )
    fig_alert.add_trace(
        go.Scatter(
            x=alert_low["date"],
            y=alert_low["production_mwh"],
            mode="markers",
            name="Sous-prod",
            marker=dict(color="red", size=10),
        )
    )
    fig_alert.add_trace(
        go.Scatter(
            x=alert_high["date"],
            y=alert_high["production_mwh"],
            mode="markers",
            name="Sur-prod",
            marker=dict(color="orange", size=10),
        )
    )
    fig_alert.add_hline(
        y=seuil_bas, line_dash="dash", line_color="red", annotation_text="Seuil Bas"
    )
    fig_alert.add_hline(
        y=seuil_haut, line_dash="dash", line_color="blue", annotation_text="Seuil Haut"
    )
    fig_alert.update_layout(
        title="Alertes Production", height=350, margin=dict(l=20, r=20, t=40, b=20)
    )
    alert_html = fig_alert.to_html(full_html=False, include_plotlyjs=False)
    alertes = []
    if not alert_low.empty:
        for i, row in alert_low.iterrows():
            alertes.append(
                f"{row['date'].date()} - Sous production {row['production_mwh']} MWh"
            )
    if not alert_high.empty:
        for i, row in alert_high.iterrows():
            alertes.append(
                f"{row['date'].date()} - Surproduction {row['production_mwh']} MWh"
            )
    alerte_banner = ""
    if alertes:
        alerte_items = "<br>".join(alertes)
        alerte_banner = f"""
		<div style='background:#ffe9e9;border:1px solid #ff7f7f;padding:10px;margin-bottom:14px;border-radius:6px;'>
			<strong style='color:#b30000;'>⚠️ ALERTES DE SEUIL</strong>
			<p style='margin:4px 0;'>{len(alertes)} dépassement(s) détecté(s) (seuil sous={seuil_bas}, seuil sur={seuil_haut}).</p>
			<p style='margin:0;line-height:1.4;'>{alerte_items}</p>
		</div>
		"""
    df_html = df.to_html(index=False, classes="table", border=1)
    meteo_prevision_html = meteo_prevision.to_html(
        index=False, classes="table", border=1
    )

    return f"""
	<html>
	<head>
		<title>Dashboard Production</title>
		<style>
			.table {{ border-collapse: collapse; width: 100%; margin-bottom: 18px; }}
			.table th, .table td {{ border: 1px solid #ccc; padding: 4px 6px; text-align: center; }}
			.table th {{ background:#f1f1f1; }}
		</style>
	</head>
	<body style='background:#f8f9fa;'>
		<div style='max-width:1100px;margin:30px auto;font-family:Arial,Helvetica,sans-serif;'>
			<h1 style='text-align:center'>Dashboard Production</h1>
			<p style='text-align:center; margin-bottom:24px;'>Voir tous les résultats merge : <a href='/merged-results'>/merged-results</a></p>
			{alerte_banner}
			<div>{prod_html}</div>
			<div>{rend_html}</div>
			<div>{rev_html}</div>
			<div>{taux_html}</div>
			<div>{sim_html}</div>
			<div>{alert_html}</div>
			<h2>Résultats du merge (production + météo historique)</h2>
			<div style='overflow:auto; max-height:380px; border: 1px solid #ddd; background: white; padding: 10px;'>{df_html}</div>
			<h2>Prévisions avec production estimée</h2>
			<div style='overflow:auto; max-height:260px; border: 1px solid #ddd; background: white; padding: 10px;'>{meteo_prevision_html}</div>
		</div>
	</body>
	</html>
	"""


@router.post("/production/saisie", tags=["Entrées"])
async def saisie_production_v2(
    data: ProductionDataModel,
    db: Session = Depends(get_db),
):
    db.execute(
        text(
            """
            INSERT INTO production (date, production_mwh, volume_eau_m3)
            VALUES (:date, :production_mwh, :volume_eau_m3)
            """
        ),
        {
            "date": data.date.isoformat(),
            "production_mwh": data.production_mwh,
            "volume_eau_m3": data.volume_eau_m3,
        },
    )
    db.commit()
    return {"status": "confirmation", "message": "Donnée enregistrée"}


@router.post("/meteo/import", tags=["Entrées"])
async def import_meteo(
    data: List[MeteoHistoriqueModel],
    db: Session = Depends(get_db),
):
    for item in data:
        db.execute(
            text(
                """
                INSERT INTO meteo (date, debit_riviere_m3s, pluviometrie_mm)
                VALUES (:date, :debit_riviere_m3s, :pluviometrie_mm)
                """
            ),
            {
                "date": item.date.isoformat(),
                "debit_riviere_m3s": item.debit_riviere_m3s,
                "pluviometrie_mm": item.pluviometrie_mm,
            },
        )
    db.commit()
    return {"status": "confirmation", "nb_records": len(data)}


@router.post("/prix/production", tags=["Configuration"])
async def set_prix(prix: float, db: Session = Depends(get_db)):
    row = db.execute(
        text(
            """
            SELECT id
            FROM centrale_parametres
            ORDER BY id DESC
            LIMIT 1
            """
        )
    ).fetchone()

    if row:
        db.execute(
            text(
                """
                UPDATE centrale_parametres
                SET prix_electricite_eur_mwh = :prix
                WHERE id = :id
                """
            ),
            {"prix": prix, "id": row[0]},
        )
    else:
        return {
            "status": "error",
            "message": "Aucune configuration centrale_parametres en base.",
        }

    db.commit()
    return {"status": "confirmation"}


@router.get("/kpi/rendement", tags=["Analyses"])
async def get_rendement_v2(
    date_start: date,
    date_end: date,
    db: Session = Depends(get_db),
):
    period_data = db.execute(
        text(
            """
            SELECT date, production_mwh, volume_eau_m3
            FROM production
            WHERE date BETWEEN :date_start AND :date_end
            ORDER BY date ASC
            """
        ),
        {"date_start": date_start.isoformat(), "date_end": date_end.isoformat()},
    ).fetchall()

    if not period_data:
        return {"message": "Aucune donnée de production sur cette période."}

    results = []
    total_prod = 0.0
    total_vol = 0.0
    for d in period_data:
        volume = float(d[2] or 0)
        production = float(d[1] or 0)
        rendement_j = production / volume if volume > 0 else 0
        results.append({"date": d[0], "rendement_journalier": rendement_j})
        total_prod += production
        total_vol += volume

    return {
        "detail_journalier": results,
        "rendement_moyen": total_prod / total_vol if total_vol > 0 else 0,
    }


@router.get("/kpi/revenu", tags=["Analyses"])
async def get_revenu(
    date_start: date,
    date_end: date,
    db: Session = Depends(get_db),
):
    prix_electricite, _, _ = _get_centrale_params(db)

    period_data = db.execute(
        text(
            """
            SELECT date, production_mwh
            FROM production
            WHERE date BETWEEN :date_start AND :date_end
            ORDER BY date ASC
            """
        ),
        {"date_start": date_start.isoformat(), "date_end": date_end.isoformat()},
    ).fetchall()

    revenus_jours = [
        {"date": d[0], "revenu": float(d[1] or 0) * prix_electricite}
        for d in period_data
    ]
    total_revenu = sum(item["revenu"] for item in revenus_jours)
    return {"revenu_total": total_revenu, "details": revenus_jours}


@router.get("/kpi/alertes", tags=["Analyses"])
async def check_alertes(
    date_start: date,
    date_end: date,
    seuil_sous: float,
    seuil_sur: float,
    db: Session = Depends(get_db),
):
    period_data = db.execute(
        text(
            """
            SELECT date, production_mwh
            FROM production
            WHERE date BETWEEN :date_start AND :date_end
            ORDER BY date ASC
            """
        ),
        {"date_start": date_start.isoformat(), "date_end": date_end.isoformat()},
    ).fetchall()

    alertes = []
    for d in period_data:
        production = float(d[1] or 0)
        if production < seuil_sous:
            alertes.append(
                {
                    "date": d[0],
                    "production": production,
                    "type": "ROUGE (Sous-production)",
                }
            )
        elif production > seuil_sur:
            alertes.append(
                {
                    "date": d[0],
                    "production": production,
                    "type": "BLEU (Surproduction)",
                }
            )
    return alertes


@router.get("/dashboard/historique", tags=["Dashboard"])
async def get_dashboard(date_start: date, date_end: date):
    return {
        "periode": {"start": date_start, "end": date_end},
        "message": "Synthèse des données historiques prête pour l'affichage graphique",
    }


@router.get("/merged-results", response_class=HTMLResponse, tags=["Dashboard"])
async def merged_results(db: Session = Depends(get_db)):
    df, meteo_prevision = _load_dashboard_data(db)
    df_html = df.to_html(index=False, classes="table", border=1)
    meteo_prevision_html = meteo_prevision.to_html(
        index=False, classes="table", border=1
    )
    return f"""
	<html>
	<head>
		<title>Résultats Merge</title>
		<style>
			.table {{ border-collapse: collapse; width: 100%; margin-bottom: 18px; }}
			.table th, .table td {{ border: 1px solid #ccc; padding: 4px 6px; text-align: center; }}
			.table th {{ background:#f1f1f1; }}
		</style>
	</head>
	<body style='background:#f8f9fa;'>
		<div style='max-width:1100px;margin:30px auto;font-family:Arial,Helvetica,sans-serif;'>
			<h1>Résultats des fichiers merge</h1>
			<p>Voici toutes les lignes du DataFrame fusionné:</p>
			<h2>Merge production + météo historique</h2>
			<div style='overflow:auto; max-height:380px; border:1px solid #ddd; background:white; padding:8px;'>{df_html}</div>
			<h2>Prévision de production estimée</h2>
			<div style='overflow:auto; max-height:260px; border:1px solid #ddd; background:white; padding:8px;'>{meteo_prevision_html}</div>
			<p><a href='/'>Retour au dashboard</a></p>
		</div>
	</body>
	</html>
	"""
