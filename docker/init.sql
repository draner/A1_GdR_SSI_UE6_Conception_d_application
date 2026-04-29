-- ============================================================
-- SI Barrage - Initialisation PostgreSQL
-- ============================================================

-- Table météo : données hydro-météorologiques mesurées
CREATE TABLE IF NOT EXISTS meteo (
    id                  SERIAL PRIMARY KEY,
    date                DATE NOT NULL,
    debit_riviere_m3s   REAL,
    pluviometrie_mm     REAL
);

-- Table prévisions météo
CREATE TABLE IF NOT EXISTS meteo_previsions (
    id                        SERIAL PRIMARY KEY,
    date_prevision            DATE NOT NULL,
    date_creation             DATE NOT NULL,
    debit_riviere_m3s_prevu   REAL,
    pluviometrie_mm_prevue    REAL
);

-- Table tickets de maintenance
CREATE TABLE IF NOT EXISTS maintenance (
    id                   SERIAL PRIMARY KEY,
    id_equipement        TEXT NOT NULL,
    nom_equipement       TEXT,
    statut               TEXT,
    description          TEXT,
    date_creation        DATE,
    ticket_id            INTEGER,
    date_intervention    DATE,
    intervenant          TEXT,
    solution             TEXT,
    duree_minutes        INTEGER,
    cout                 REAL,
    pieces_changees      TEXT
);

-- Table production électrique
CREATE TABLE IF NOT EXISTS production (
    id               SERIAL PRIMARY KEY,
    date             DATE NOT NULL,
    production_mwh   REAL,
    volume_eau_m3    INTEGER
);

-- Table interventions réalisées
CREATE TABLE IF NOT EXISTS intervention (
    id                   SERIAL PRIMARY KEY,
    id_equipement        TEXT NOT NULL,
    date_intervention    DATE NOT NULL,
    intervenant          TEXT,
    probleme             TEXT,
    solution             TEXT
);

-- Table paramètres statiques de la centrale
CREATE TABLE IF NOT EXISTS centrale_parametres (
    id                        SERIAL PRIMARY KEY,
    nombre_turbines           INTEGER NOT NULL CHECK (nombre_turbines >= 0),
    puissance_nominale_mw     REAL    NOT NULL CHECK (puissance_nominale_mw >= 0),
    prix_electricite_eur_mwh  REAL    NOT NULL CHECK (prix_electricite_eur_mwh >= 0)
);

-- Données de configuration initiales
INSERT INTO centrale_parametres (nombre_turbines, puissance_nominale_mw, prix_electricite_eur_mwh)
VALUES (4, 120.0, 85.0);
