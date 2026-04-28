# Documentation API - Module Production

## Vue d'ensemble

Le module Production fournit une API FastAPI complète pour la gestion et l'analyse des données de production d'un barrage hydroélectrique. Il inclut des fonctionnalités de saisie de données, d'analyse KPI, de visualisation et de configuration.

## Modèles de données

### ProductionDataModel
```python
{
    "date": "2024-01-15",  # Date de la mesure (YYYY-MM-DD)
    "production_mwh": 3500.0,  # Production en mégawatts-heure
    "volume_eau_m3": 7000000.0  # Volume d'eau en mètres cubes
}
```

### MeteoHistoriqueModel
```python
{
    "date": "2024-01-15",  # Date de la mesure (YYYY-MM-DD)
    "debit_riviere_m3s": 142.8,  # Débit de la rivière en m³/s
    "pluviometrie_mm": 2.1  # Pluviométrie en millimètres
}
```

## Endpoints API

### Dashboard Principal

#### `GET /`
**Description**: Affiche le dashboard complet avec graphiques et tableaux de bord interactifs.

**Réponse**: Page HTML avec :
- Graphique de production (MWh)
- Graphique d'efficacité hydraulique (MWh/m³)
- Graphique des revenus journaliers (€)
- Graphique du taux de charge (%)
- Graphique de simulation de prévision
- Graphique des alertes de seuil
- Tableaux des données fusionnées

### Saisie de données

#### `POST /production/saisie`
**Tag**: Entrées

**Description**: Enregistre une nouvelle donnée de production.

**Corps de la requête**:
```json
{
    "date": "2024-01-15",
    "production_mwh": 3500.0,
    "volume_eau_m3": 7000000.0
}
```

**Réponse**:
```json
{
    "status": "confirmation",
    "message": "Donnée enregistrée"
}
```

#### `POST /meteo/import`
**Tag**: Entrées

**Description**: Importe plusieurs données météorologiques historiques.

**Corps de la requête**:
```json
[
    {
        "date": "2024-01-15",
        "debit_riviere_m3s": 142.8,
        "pluviometrie_mm": 2.1
    }
]
```

**Réponse**:
```json
{
    "status": "confirmation",
    "nb_records": 1
}
```

### Configuration

#### `POST /prix/production`
**Tag**: Configuration

**Description**: Définit le prix de l'électricité pour les calculs de revenus.

**Corps de la requête**:
```json
120.0
```

**Réponse**:
```json
{
    "status": "confirmation"
}
```

### Analyses KPI

#### `GET /kpi/rendement`
**Tag**: Analyses

**Description**: Calcule le rendement hydraulique sur une période donnée.

**Paramètres de requête**:
- `date_start`: Date de début (YYYY-MM-DD)
- `date_end`: Date de fin (YYYY-MM-DD)

**Exemple**: `/kpi/rendement?date_start=2024-01-01&date_end=2024-01-10`

**Réponse**:
```json
{
    "detail_journalier": [
        {
            "date": "2024-01-01",
            "rendement_journalier": 0.0005
        }
    ],
    "rendement_moyen": 0.000512
}
```

#### `GET /kpi/revenu`
**Tag**: Analyses

**Description**: Calcule les revenus sur une période donnée.

**Paramètres de requête**:
- `date_start`: Date de début (YYYY-MM-DD)
- `date_end`: Date de fin (YYYY-MM-DD)

**Exemple**: `/kpi/revenu?date_start=2024-01-01&date_end=2024-01-10`

**Réponse**:
```json
{
    "revenu_total": 420000.0,
    "details": [
        {
            "date": "2024-01-01",
            "revenu": 300000.0
        }
    ]
}
```

#### `GET /kpi/alertes`
**Tag**: Analyses

**Description**: Détecte les alertes de sous/sur-production selon les seuils définis.

**Paramètres de requête**:
- `date_start`: Date de début (YYYY-MM-DD)
- `date_end`: Date de fin (YYYY-MM-DD)
- `seuil_sous`: Seuil de sous-production (MWh)
- `seuil_sur`: Seuil de sur-production (MWh)

**Exemple**: `/kpi/alertes?date_start=2024-01-01&date_end=2024-01-10&seuil_sous=3000&seuil_sur=4500`

**Réponse**:
```json
[
    {
        "date": "2024-01-01",
        "production": 2500.0,
        "type": "ROUGE (Sous-production)"
    },
    {
        "date": "2024-01-07",
        "production": 4800.0,
        "type": "BLEU (Surproduction)"
    }
]
```

### Dashboard

#### `GET /dashboard/historique`
**Tag**: Dashboard

**Description**: Prépare les données pour l'affichage du dashboard historique.

**Paramètres de requête**:
- `date_start`: Date de début (YYYY-MM-DD)
- `date_end`: Date de fin (YYYY-MM-DD)

**Réponse**:
```json
{
    "periode": {
        "start": "2024-01-01",
        "end": "2024-01-10"
    },
    "message": "Synthèse des données historiques prête pour l'affichage graphique"
}
```

#### `GET /merged-results`
**Tag**: Dashboard

**Description**: Affiche les résultats des fusions de données (production + météo).

**Réponse**: Page HTML avec les tableaux des données fusionnées.

## Constantes et calculs

Le module utilise les constantes suivantes pour les calculs :

- **Prix de l'électricité**: 120 €/MWh (configurable)
- **Nombre de turbines**: 4
- **Puissance nominale par turbine**: 50 MW
- **Seuils par défaut**:
  - Sous-production: 3000 MWh
  - Sur-production: 4500 MWh

## Calculs automatiques

### Efficacité hydraulique
```
efficacité = production_mwh / volume_eau_m3
```

### Production maximale théorique
```
production_max = nombre_turbines × puissance_nominal × 24_heures
```

### Taux de charge
```
taux_charge = (production_réelle / production_max) × 100
```

### Revenus
```
revenu = production_mwh × prix_électricité
```

## Données de démonstration

Le module inclut des données de démonstration pour :
- Production historique (10 jours)
- Données météorologiques historiques
- Prévisions météorologiques avec calculs de production estimée

## Utilisation typique

1. **Configuration**: Définir le prix de l'électricité via `/prix/production`
2. **Saisie**: Alimenter les données via `/production/saisie` et `/meteo/import`
3. **Analyse**: Consulter les KPI via les endpoints `/kpi/*`
4. **Visualisation**: Accéder au dashboard via `/` ou `/merged-results`

## Technologies utilisées

- **FastAPI**: Framework API
- **Pydantic**: Validation des modèles de données
- **Pandas**: Manipulation des données
- **Plotly**: Génération de graphiques interactifs
- **HTML/CSS**: Interface utilisateur du dashboard