# Tutoriel : lancer SI Barrage en mode PostgreSQL avec Docker Compose

Ce tutoriel explique comment démarrer l'application en mode PostgreSQL sur Windows, avec Docker Desktop et `docker compose`.

## 1. Prérequis

Avant de commencer, vérifiez que vous avez :

- Windows 10 ou Windows 11
- Un compte avec droits d'installation sur la machine
- Le dépôt du projet déjà cloné en local
- Python installé si vous souhaitez aussi lancer l'API en dehors de Docker

## 2. Installer Docker Desktop

1. Ouvrez le site officiel de Docker Desktop et téléchargez l'installeur Windows.
2. Lancez l'installation.
3. Gardez les options par défaut, sauf si votre environnement impose une configuration spécifique.
4. À la fin, démarrez Docker Desktop.

Sur Windows, Docker Desktop doit être ouvert et fonctionnel avant de lancer `docker compose`.
L'icône Docker dans la barre des tâches doit être visible et indiquer que le moteur est prêt.

### Vérification rapide

Dans un terminal PowerShell, exécutez :

```powershell
docker --version
docker compose version
```

Si les deux commandes répondent correctement, Docker est prêt.

## 3. Comprendre le mode PostgreSQL

Le projet peut fonctionner avec SQLite en local, mais le mode PostgreSQL est celui prévu pour le conteneur Docker.

Le fichier `docker-compose.yml` démarre :

- une base PostgreSQL nommée `barrage`
- un générateur de données temps réel

Le service PostgreSQL expose le port `5432` sur la machine locale.

## 4. Configurer le fichier `.env`

L'application lit la variable `DATABASE_URL` au démarrage. Dans ce projet, le fichier chargé est `si_barrage/.env`.

### 4.1 Créer le fichier

Si le fichier n'existe pas encore, copiez le modèle fourni à la racine du dépôt :

```powershell
Copy-Item .env.example si_barrage\.env
```

Vous pouvez aussi créer le fichier manuellement si vous préférez.

### 4.2 Contenu attendu

Pour le mode PostgreSQL avec Docker Compose, le fichier `si_barrage/.env` doit contenir au minimum :

```env
DATABASE_URL=postgresql://barrage_user:barrage_pass@localhost:5432/barrage
```

Points importants :

- `localhost` est correct quand l'API est lancée sur votre machine, pas dans un conteneur
- le port doit rester `5432` sauf si vous avez modifié le `docker-compose.yml`
- si `DATABASE_URL` est absent, l'application retombe sur SQLite local

### 4.3 Passer temporairement en SQLite

Si vous voulez revenir au mode local sans Docker, remplacez la valeur par :

```env
# DATABASE_URL=sqlite:///./barrage.db
```

## 5. Démarrer la base PostgreSQL

Depuis la racine du dépôt, lancez :

```powershell
docker compose up -d db
```

Cette commande démarre uniquement la base PostgreSQL.

Le premier lancement crée automatiquement la base `barrage` et exécute `docker/init.sql`.

### Vérifier que la base est prête

```powershell
docker compose ps
```

Le service `db` doit apparaître avec un état sain ou en cours de démarrage normal.

## 6. Démarrer l'application FastAPI

Ouvrez un deuxième terminal PowerShell dans la racine du projet, puis lancez :

```powershell
uvicorn si_barrage.main:app --reload
```

Au démarrage, l'application lit `si_barrage/.env`, récupère `DATABASE_URL` et se connecte à PostgreSQL.

### Tester la connexion

Une fois l'application lancée, ouvrez :

- `http://127.0.0.1:8000` pour l'application
- `http://127.0.0.1:8000/docs` pour la documentation API
- `http://127.0.0.1:8000/db` pour vérifier la connexion à la base

La route `/db` doit afficher la liste des tables PostgreSQL créées par le script d'initialisation.

## 7. Lancer tout le stack Docker

Si vous voulez démarrer la base PostgreSQL et le générateur de données en une seule commande, utilisez :

```powershell
docker compose up -d
```

Ensuite, lancez l'API FastAPI en local avec `uvicorn` comme indiqué plus haut.

## 8. Arrêter proprement

Pour arrêter les conteneurs :

```powershell
docker compose down
```

Si vous voulez aussi supprimer les données persistées dans le volume PostgreSQL, utilisez :

```powershell
docker compose down -v
```

Attention, cette seconde commande supprime les données de la base.

## 9. Dépannage rapide

### Le port 5432 est déjà utilisé

Un autre PostgreSQL est peut-être déjà lancé sur votre machine. Dans ce cas, arrêtez-le ou modifiez le port exposé dans `docker-compose.yml`.

### Docker Desktop n'est pas démarré

`docker compose` ne fonctionnera pas tant que Docker Desktop n'est pas ouvert et prêt.

### L'application retombe sur SQLite

Vérifiez que `si_barrage/.env` existe bien et que `DATABASE_URL` est défini avec l'URL PostgreSQL attendue.

### La base est vide au premier lancement

Le script `docker/init.sql` n'est exécuté qu'au premier démarrage du volume PostgreSQL. Si vous voulez recommencer depuis zéro, supprimez le volume avec `docker compose down -v` puis relancez `docker compose up -d`.
