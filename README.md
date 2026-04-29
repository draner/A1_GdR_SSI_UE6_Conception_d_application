# Projet Fil Rouge : Conception d'un Système d'Information pour un Barrage Hydroélectrique

Bienvenue dans le projet fil rouge du cours "Conception d'applications" ! Ce projet est conçu pour vous initier aux principes fondamentaux du génie logiciel, de l'analyse des besoins à la livraison d'un produit fonctionnel, dans un contexte de cybersécurité.

## 🎯 Objectifs Pédagogiques

À la fin de ce projet, vous serez capable de :

- **Traduire un besoin métier** en spécifications techniques.
- **Concevoir et modéliser** une application et sa base de données.
- **Développer une application** en Python en utilisant des frameworks modernes (FastAPI).
- **Collaborer efficacement** en équipe à l'aide de Git et GitHub.
- **Intégrer et tester** différents modules pour construire un système cohérent.
- **Utiliser l'Intelligence Artificielle** comme un outil d'aide au développement.
- **Comprendre les bases du déploiement** d'applications (avec Docker).

## contexte

Vous êtes une équipe d'ingénieurs missionnée par une PME qui gère un barrage hydroélectrique. Votre objectif est de développer un Système d'Information (SI) pour moderniser la gestion de ses opérations.

Le projet se déroule dans un environnement simulé (CyberRange) et se concentre sur la **conception fonctionnelle** de l'application. Bien que vous soyez dans un parcours de cybersécurité, l'accent est mis ici sur la construction d'une application qui répond correctement aux besoins, et non sur la sécurisation de l'infrastructure.

## 🗂️ Organisation du Projet

Le projet est divisé en trois modules principaux, chaque module étant développé par une équipe dédiée.

### Équipes et Modules

- **Équipe 1 : Module Météo et Hydrologie**
  - **Mission :** Suivre le débit de la rivière, la pluviométrie et fournir des prévisions.
  - **Fonctionnalités clés :** Dashboard de suivi, historique des données, alertes de crue.

- **Équipe 2 : Module de Maintenance**
  - **Mission :** Gérer la maintenance préventive et corrective des équipements du barrage.
  - **Fonctionnalités clés :** Gestion des tickets d'intervention, suivi du statut des équipements, historique des maintenances.

- **Équipe 3 : Module de Production Énergétique**
  - **Mission :** Simuler et suivre la production d'électricité.
  - **Fonctionnalités clés :** Graphiques de production (temps réel et historique), calcul de KPIs (Key Performance Indicators), système d'alertes en cas de sous-production ou sur-production.

### Le Défi de l'Intégration

Chaque équipe développe son module de manière indépendante. Cependant, tous les modules devront à la fin être intégrés dans une **application principale commune**. Cette intégration nécessitera de respecter des **contrats d'interface** et un **schéma de base de données partagé**.

## 💻 Stack Technique

- **Langage :** Python 3
- **Framework Backend :** FastAPI
- **Base de données :** SQLite (pour le développement local), PostgreSQL (en production dans le CyberRange)
- **Interface Utilisateur (UI) :** Une simple interface graphique (une interface web) sera développée.
- **Contrôle de version :** Git et GitHub
- **Déploiement :** Docker

## 🚀 Démarrer le Projet

Pour lancer l'application en mode PostgreSQL avec Docker Compose, consultez le tutoriel détaillé : [docs/tutoriel_lancement_postgresql_docker.md](docs/tutoriel_lancement_postgresql_docker.md).

1. **Forker ce dépôt :** Chaque équipe doit créer un "fork" de ce dépôt. C'est votre propre version du projet sur laquelle vous travaillerez.
2. **Cloner votre fork :** Clonez le dépôt forké sur votre machine locale pour commencer à travailler.
  
    ```bash
    git clone https://github.com/VOTRE_NOM_UTILISATEUR/A1_GdR_SSI_UE6_Conception_d_application.git
    ```

3. **Créer une branche pour votre équipe :**
  
  ```bash
    git checkout -b equipe-X-module-Y
  ```

Remplacez `X` par le numéro de votre équipe et `Y` par le nom de votre module.

## 📅 Planning Général

- **Février :** Analyse des besoins, conception du schéma de la base de données et définition des interfaces entre les modules.
- **Mars :** Développement des modules en parallèle par chaque équipe.
- **Avril :** Intégration des modules dans l'application principale.
- **Mai :** Phase de tests, packaging de l'application et présentation finale.

## 🤖 Utilisation de l'IA dans le Développement

L'utilisation d'outils d'IA comme GitHub Copilot ou ChatGPT est encouragée, mais doit être faite de manière réfléchie. L'IA est un **assistant**, pas un remplaçant. Vous êtes responsable de la qualité, de la pertinence et de la correction du code produit.

**Bonnes pratiques :**

- Utilisez l'IA pour générer du code répétitif ("boilerplate").
- Demandez des suggestions pour résoudre des problèmes algorithmiques complexes.
- **Ne copiez jamais-collez du code sans le comprendre.**
- **Validez et testez toujours** le code généré par une IA.

Bon courage à toutes les équipes !
