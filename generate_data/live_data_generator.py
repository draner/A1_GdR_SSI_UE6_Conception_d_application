#!/usr/bin/env python3
"""
Générateur de données temps réel pour la base PostgreSQL du SI Barrage.

À chaque intervalle, le script insère :
  - un jour de données météo (débit, pluviométrie)
  - un jour de données de production (MWh, volume eau)
  - des prévisions météo glissantes sur 5 jours
  - occasionnellement un ticket de maintenance ou une intervention

La date simulée avance d'un jour à chaque cycle : l'application verra
ainsi de nouvelles données arriver en continu.

Variables d'environnement :
  DATABASE_URL        URL de connexion PostgreSQL
                      (défaut : postgresql://barrage_user:barrage_pass@localhost:5432/barrage)
  GENERATION_INTERVAL Secondes entre chaque cycle (défaut : 15)
"""

import logging
import os
import random
import time
from datetime import date, timedelta
from typing import Optional

import psycopg2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("si_barrage.generator")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://barrage_user:barrage_pass@localhost:5432/barrage",
)
GENERATION_INTERVAL = int(os.environ.get("GENERATION_INTERVAL", "15"))

# Référentiel des équipements de la centrale
EQUIPEMENTS = [
    ("T1", "Turbine 1"),
    ("T2", "Turbine 2"),
    ("T3", "Turbine 3"),
    ("T4", "Turbine 4"),
    ("VAN1", "Vanne principale"),
    ("GEN1", "Générateur 1"),
]
STATUTS = ["En cours", "Terminé", "En attente"]
INTERVENANTS = ["Alice Martin", "Bob Dupont", "Claire Leroy", "David Bernard"]
PROBLEMES = [
    "Vibrations anormales détectées",
    "Fuite d'huile constatée",
    "Bruit inhabituel signalé",
    "Usure prématurée des paliers",
    "Surtension électrique",
]


def ensure_maintenance_schema(conn: psycopg2.extensions.connection) -> None:
    """
    Aligne la table maintenance PostgreSQL sur la structure fonctionnelle SQLite.

    Utile quand la base a ete creee avant l'ajout des nouvelles colonnes.
    """
    cur = conn.cursor()
    cur.execute(
        """
        ALTER TABLE maintenance
        ADD COLUMN IF NOT EXISTS ticket_id INTEGER,
        ADD COLUMN IF NOT EXISTS date_intervention DATE,
        ADD COLUMN IF NOT EXISTS intervenant TEXT,
        ADD COLUMN IF NOT EXISTS solution TEXT,
        ADD COLUMN IF NOT EXISTS duree_minutes INTEGER,
        ADD COLUMN IF NOT EXISTS cout REAL,
        ADD COLUMN IF NOT EXISTS pieces_changees TEXT
        """
    )
    conn.commit()
    cur.close()


def insert_maintenance_row(
    cur: psycopg2.extensions.cursor,
    *,
    id_equipement: str,
    nom_equipement: str,
    statut: str,
    description: str,
    date_creation: date,
    ticket_id: int | None = None,
    date_intervention: date | None = None,
    intervenant: str | None = None,
    solution: str | None = None,
    duree_minutes: int | None = None,
    cout: float | None = None,
    pieces_changees: str | None = None,
) -> int:
    """Insere une ligne maintenance complete et renvoie son id."""
    cur.execute(
        """
        INSERT INTO maintenance (
            id_equipement,
            nom_equipement,
            statut,
            description,
            date_creation,
            ticket_id,
            date_intervention,
            intervenant,
            solution,
            duree_minutes,
            cout,
            pieces_changees
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            id_equipement,
            nom_equipement,
            statut,
            description,
            date_creation,
            ticket_id,
            date_intervention,
            intervenant,
            solution,
            duree_minutes,
            cout,
            pieces_changees,
        ),
    )
    inserted = cur.fetchone()
    if inserted is None:
        raise RuntimeError("Insertion maintenance echouee: id introuvable")
    return int(inserted[0])


SOLUTIONS = [
    "Remplacement des joints",
    "Rééquilibrage du rotor",
    "Resserrage des boulons de fixation",
    "Étalonnage des capteurs",
    "Changement des filtres à huile",
]


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def seed_historical_data(conn: psycopg2.extensions.connection) -> None:
    """Insère 30 jours de données historiques si la table meteo est vide."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM meteo")
    count_row = cur.fetchone()
    count = int(count_row[0]) if count_row else 0
    if count > 0:
        log.info("Table 'meteo' : %d ligne(s) existante(s) — seed ignoré.", count)
        cur.close()
        return

    today = date.today()
    start = today - timedelta(days=30)
    log.info("Seed historique : insertion de 30 jours (%s → %s)…", start, today)

    for i in range(30):
        d = start + timedelta(days=i)
        debit = round(random.uniform(80.0, 200.0), 1)
        pluv = round(random.uniform(0.0, 30.0), 1)

        cur.execute(
            "INSERT INTO meteo (date, debit_riviere_m3s, pluviometrie_mm) VALUES (%s, %s, %s)",
            (d, debit, pluv),
        )
        log.debug("  meteo        %s | débit=%.1f m³/s  pluv=%.1f mm", d, debit, pluv)

        prod = round(debit * random.uniform(15.0, 25.0), 1)
        vol = int(prod * random.uniform(1800.0, 2200.0))
        cur.execute(
            "INSERT INTO production (date, production_mwh, volume_eau_m3) VALUES (%s, %s, %s)",
            (d, prod, vol),
        )
        log.debug("  production   %s | prod=%.1f MWh  vol=%d m³", d, prod, vol)

    # Quelques tickets de maintenance initiaux au format fonctionnel
    for _ in range(5):
        equip_id, equip_name = random.choice(EQUIPEMENTS)
        statut = random.choice(STATUTS)
        desc = random.choice(PROBLEMES)
        tech = random.choice(INTERVENANTS)
        dt_creation = today - timedelta(days=random.randint(1, 30))
        dt_intervention = dt_creation + timedelta(days=random.randint(0, 2))
        solution = random.choice(SOLUTIONS)
        duree = random.randint(30, 180) if statut == "Terminé" else 0
        cout = round(random.uniform(20.0, 300.0), 1) if statut == "Terminé" else 0.0
        row_id = insert_maintenance_row(
            cur,
            id_equipement=equip_id,
            nom_equipement=equip_name,
            statut=statut,
            description=desc,
            date_creation=dt_creation,
            date_intervention=dt_intervention,
            intervenant=tech,
            solution=solution,
            duree_minutes=duree,
            cout=cout,
            pieces_changees="",
        )
        # Meme comportement que le formulaire de tickets: ticket_id = id.
        cur.execute(
            "UPDATE maintenance SET ticket_id = %s WHERE id = %s", (row_id, row_id)
        )
        log.debug("  maintenance  %s [%s] — %s", equip_name, statut, desc)

    conn.commit()
    cur.close()
    log.info("Seed historique terminé avec succès.")


def generate_new_day(conn: psycopg2.extensions.connection) -> None:
    """Avance la simulation d'un jour et insère les nouvelles données."""
    cur = conn.cursor()

    # Déterminer la prochaine date à simuler
    cur.execute("SELECT MAX(date) FROM meteo")
    last_date_row = cur.fetchone()
    last_date: Optional[date] = (
        last_date_row[0] if last_date_row and last_date_row[0] else None
    )
    next_date: date = (last_date + timedelta(days=1)) if last_date else date.today()

    log.info("── Nouveau cycle : date simulée %s ──", next_date)

    # — Météo —
    debit = round(random.uniform(80.0, 200.0), 1)
    pluv = round(random.uniform(0.0, 30.0), 1)
    cur.execute(
        "INSERT INTO meteo (date, debit_riviere_m3s, pluviometrie_mm) VALUES (%s, %s, %s)",
        (next_date, debit, pluv),
    )
    log.info("  [meteo]       débit=%.1f m³/s | pluviométrie=%.1f mm", debit, pluv)

    # — Production —
    prod = round(debit * random.uniform(15.0, 25.0), 1)
    vol = int(prod * random.uniform(1800.0, 2200.0))
    cur.execute(
        "INSERT INTO production (date, production_mwh, volume_eau_m3) VALUES (%s, %s, %s)",
        (next_date, prod, vol),
    )
    log.info("  [production]  production=%.1f MWh | volume=%d m³", prod, vol)

    # — Prévisions glissantes sur 5 jours —
    for i in range(1, 6):
        forecast_date = next_date + timedelta(days=i)
        f_debit = round(random.uniform(80.0, 200.0), 1)
        f_pluv = round(random.uniform(0.0, 30.0), 1)
        cur.execute(
            """
            INSERT INTO meteo_previsions
                (date_prevision, date_creation, debit_riviere_m3s_prevu, pluviometrie_mm_prevue)
            VALUES (%s, %s, %s, %s)
            """,
            (forecast_date, next_date, f_debit, f_pluv),
        )
        log.debug(
            "  [prévision J+%d] %s | débit=%.1f m³/s | pluv=%.1f mm",
            i,
            forecast_date,
            f_debit,
            f_pluv,
        )
    log.info("  [prévisions]  5 prévisions glissantes insérées")

    # — Maintenance (20 % de chances) —
    if random.random() < 0.20:
        equip_id, equip_name = random.choice(EQUIPEMENTS)
        desc = random.choice(PROBLEMES)
        row_id = insert_maintenance_row(
            cur,
            id_equipement=equip_id,
            nom_equipement=equip_name,
            statut="En cours",
            description=desc,
            date_creation=next_date,
            date_intervention=next_date,
            intervenant=random.choice(INTERVENANTS),
            solution="Diagnostic en cours",
            duree_minutes=0,
            cout=0.0,
            pieces_changees="",
        )
        cur.execute(
            "UPDATE maintenance SET ticket_id = %s WHERE id = %s", (row_id, row_id)
        )
        log.info("  [maintenance] Nouveau ticket — %s : %s", equip_name, desc)

    # — Intervention (15 % de chances) —
    if random.random() < 0.15:
        equip_id, equip_name = random.choice(EQUIPEMENTS)
        intervenant = random.choice(INTERVENANTS)
        probleme = random.choice(PROBLEMES)
        solution = random.choice(SOLUTIONS)
        duree = random.randint(30, 180)
        cout = round(random.uniform(20.0, 300.0), 1)
        pieces = ""

        cur.execute(
            """
            INSERT INTO intervention
                (id_equipement, date_intervention, intervenant, probleme, solution)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (equip_id, next_date, intervenant, probleme, solution),
        )

        # Replication dans maintenance: l'app maintenance consomme cette table.
        insert_maintenance_row(
            cur,
            id_equipement=equip_id,
            nom_equipement=equip_name,
            statut="Terminé",
            description=probleme,
            date_creation=next_date,
            date_intervention=next_date,
            intervenant=intervenant,
            solution=solution,
            duree_minutes=duree,
            cout=cout,
            pieces_changees=pieces,
        )

        log.info(
            "  [intervention] %s par %s : %s → %s",
            equip_name,
            intervenant,
            probleme,
            solution,
        )

    conn.commit()
    cur.close()
    log.info("  Commit OK — prochain cycle dans %ds", GENERATION_INTERVAL)


def main() -> None:
    db_host = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
    log.info(
        "Générateur SI Barrage démarré | intervalle=%ds | db=%s",
        GENERATION_INTERVAL,
        db_host,
    )

    # Attente de la disponibilité de la base (utile au démarrage du conteneur)
    conn = None
    for attempt in range(30):
        try:
            conn = get_connection()
            log.info("Connexion PostgreSQL établie.")
            break
        except Exception as exc:
            log.warning("Tentative %d/30 échouée : %s", attempt + 1, exc)
            time.sleep(2)
    else:
        log.error("Impossible de se connecter à la base après 30 tentatives. Arrêt.")
        raise SystemExit(1)

    try:
        ensure_maintenance_schema(conn)
        seed_historical_data(conn)
        while True:
            generate_new_day(conn)
            time.sleep(GENERATION_INTERVAL)
    except KeyboardInterrupt:
        print("Générateur arrêté.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
