````markdown
# 🏥 Plateforme de Rendez-vous Médicaux

Système de **prise de rendez-vous médicaux** basé sur une **architecture distribuée** utilisant **Flask**, **RPC**, et une **base de données MySQL partagée**.

Le projet peut être exécuté :
- en **mode manuel (développement local)**
- en **mode Docker & Docker Compose (recommandé)**

---

## 🧱 Architecture Générale

- App Générale (Gateway)
- Service Admin
- Service Médecin
- Service Patient
- RPC intégré dans chaque service
- Base de données MySQL commune

---

# 🚀 Version 1 — Lancement Manuel (Mode Développement)

### 📌 Prérequis
- Python 3.10+
- MySQL installé localement
- Git

---

## 🔧 Installation & Configuration

```bash
# 1. Cloner le projet
git clone https://github.com/votre-username/medicare-booking-system.git
cd medicare-booking-system

# 2. Installer les dépendances
pip install -r requirements.txt
````

---

## 🗄️ Configuration Base de Données

Créer un fichier `.env` à la racine du projet :

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medicare_unified
DB_USER=root
DB_PASSWORD=root
```

---

## 🔍 Tester la connexion à la base de données

```bash
python -c "from database.connection import test_connection; test_connection()"
```

---

## 🧪 Initialiser la base de données

```bash
python scripts/setup_database.py
```

---

## ▶️ Lancer toutes les applications (recommandé)

Le projet fournit un script automatique :

```bash
start_all.bat
```

Ce script démarre :

* l’App Générale
* le Service Admin
* le Service Médecin
* le Service Patient

Chaque application s’exécute dans son propre terminal et sur un port dédié.

---

## 🌐 Accès aux services (manuel)

| Service      | URL                                            |
| ------------ | ---------------------------------------------- |
| App Générale | [http://localhost:5000](http://localhost:5000) |
| Médecin      | [http://localhost:5001](http://localhost:5001) |
| Patient      | [http://localhost:5002](http://localhost:5002) |
| Admin        | [http://localhost:5003](http://localhost:5003) |

---

# 🐳 Version 2 — Docker & Docker Compose (Recommandée)

### 📌 Prérequis

* Docker Desktop
* Docker Compose v2 (`docker compose`)

---

## 🧩 Fonctionnement Docker

* Chaque service Flask est exécuté dans son propre conteneur
* RPC démarre automatiquement avec chaque service
* MySQL est containerisé
* La base de données est importée automatiquement depuis `database/db.sql`

---

## ▶️ Lancer le projet avec Docker

```bash
# Arrêter et nettoyer les anciens conteneurs et volumes
docker compose down -v

# Construire et lancer tous les services
docker compose up --build
```

Ou en arrière-plan :

```bash
docker compose up -d --build
```

---

## 🌐 Accès aux services (Docker)

| Service      | URL                                            |
| ------------ | ---------------------------------------------- |
| App Générale | [http://localhost:5000](http://localhost:5000) |
| Médecin      | [http://localhost:5001](http://localhost:5001) |
| Patient      | [http://localhost:5002](http://localhost:5002) |
| Admin        | [http://localhost:5003](http://localhost:5003) |
| MySQL        | localhost:3307                                 |

---

## 🗄️ Base de Données (Docker)

* Nom : `medicare_unified`
* Import automatique : `database/db.sql`
* Accès externe :

  * Host : `localhost`
  * Port : `3307`
  * User : `root`
  * Password : `root`

---

## ⛔ Arrêter les services Docker

```bash
docker compose down
```

---

## 🧪 Dépendances principales

* Flask
* PyJWT
* mysql-connector-python
* python-dotenv
* Docker / Docker Compose

---
## 🔐 Comptes de test & Codes d’accès

### 📋 Comptes existants

| Nom      | Rôle     | Email              | Code d’accès |
|----------|----------|--------------------|--------------|
| Mouad    | ADMIN    | mouad@gmail.admin  | 12345        |
| Hamza   | MEDECIN  | hamza@gmail.com    | 00000        |
| Mohamed | PATIENT  | mohamed@gg.com     | 00000        |

---

## 📝 Inscription & Gestion des utilisateurs

- ✅ **L’inscription (Register) est disponible uniquement pour les PATIENTS**
- ❌ Les **Médecins et Admins ne peuvent pas s’inscrire eux-mêmes**

### 👨‍⚕️👤 Création des comptes
- Les comptes **Médecin** et **Patient** peuvent également être **créés depuis l’espace Admin**
- Lorsqu’un compte est créé par l’Admin, le **code d’accès par défaut est : `00000`**





