Parfait 👍
Voici **le contenu COMPLET de `auth.md`**, **en Markdown**, **prêt à copier-coller**, incluant **login, récupération JWT, autorisation par rôle et logout**.
Tu peux le coller tel quel dans **Docs/auth.md**.

---

````markdown
# 🔐 Authentification & Autorisation (JWT)
## Architecture : Auth REST + RPC REST + RPC XML

---

## 📌 Vue d’ensemble

- L’authentification est **centralisée** dans l’application **Auth (REST)**.
- Après un login réussi, un **JWT** est généré.
- Le JWT est stocké dans un **cookie HTTPOnly** nommé :

```text
access_token
````

* Ce cookie est envoyé automatiquement avec chaque requête HTTP.
* Les services peuvent être :

  * RPC REST (JSON)
  * RPC XML
  * REST classique
    ➡️ **Le JWT est indépendant du type de RPC**.

---

## 🧾 Contenu du JWT

Exemple de payload décodé :

```json
{
  "user_id": 7,
  "role": "MEDECIN",
  "exp": 1730000000
}
```

Champs utilisés :

* `user_id`
* `role`

---

## 🔑 Login (Auth REST)

### Endpoint

```http
POST /api/rpc
```

### Body (JSON)

```json
{
  "method": "login",
  "params": {
    "email": "user@test.com",
    "password": "123456"
  }
}
```

### Résultat

* Création du JWT
* Stockage dans le cookie `access_token`
* Redirection selon le rôle :

  * `PATIENT` → `http://localhost:5001/patient/dashboard`
  * `MEDECIN` → `http://localhost:5002/medecin/dashboard`
  * `ADMIN` → `http://localhost:5003/admin/dashboard`

---

## 🧩 Cas 1 — Service REST / RPC REST (Flask)

### Fonction utilitaire (recommandée)

```python
import jwt
from flask import request

SECRET_KEY = "secret123"

def get_current_user():
    token = request.cookies.get("access_token")

    if not token:
        return None, None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("user_id"), payload.get("role")
    except Exception:
        return None, None
```

### Utilisation dans une route

```python
from flask import redirect, render_template

@patient_bp.route("/dashboard")
def dashboard():
    user_id, role = get_current_user()

    if not user_id or role != "PATIENT":
        return redirect("http://localhost:5000/login")

    return render_template(
        "patient/dashboard.html",
        user_id=user_id,
        role=role
    )
```

---

## 🧩 Cas 2 — Service RPC XML (SimpleXMLRPCServer)

⚠️ Le serveur RPC XML ne fournit pas `request` comme Flask.
Le JWT est toutefois présent dans les **headers HTTP (Cookie)**.

### Extraction du JWT depuis les headers

```python
import jwt

SECRET_KEY = "secret123"

def extract_user_from_cookie(headers):
    cookie = headers.get("Cookie")
    if not cookie:
        return None, None

    for part in cookie.split(";"):
        if part.strip().startswith("access_token="):
            token = part.strip().split("=", 1)[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                return payload.get("user_id"), payload.get("role")
            except Exception:
                return None, None

    return None, None
```

### Utilisation dans une fonction RPC XML

```python
def liste_rdv():
    headers = server.RequestHandlerClass.headers
    user_id, role = extract_user_from_cookie(headers)

    if role != "ADMIN":
        return {"error": "UNAUTHORIZED"}

    return [...]
```

---

## 🔐 Autorisation par rôle (OBLIGATOIRE)

Chaque service doit vérifier le rôle :

| Service | Rôle requis |
| ------- | ----------- |
| Admin   | `ADMIN`     |
| Médecin | `MEDECIN`   |
| Patient | `PATIENT`   |

---

## 🚪 Logout (déconnexion)

### Principe

* Supprimer les cookies JWT côté client
* Rediriger vers la page de login

### Endpoint (Auth REST)

```http
POST /api/rpc
```

### Body

```json
{
  "method": "logout"
}
```

### Implémentation serveur (exemple)

```python
from flask import make_response, jsonify

def logout():
    response = make_response(jsonify({
        "success": True,
        "redirect": "/login"
    }))
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return response
```

---

## ❌ Ce qu’il ne faut PAS faire

* ❌ Stocker le rôle dans la session Flask
* ❌ Relire l’utilisateur depuis la DB à chaque requête
* ❌ Dépendre du type de RPC (XML vs REST)
* ❌ Ignorer la vérification du rôle

---

## 🧠 Pourquoi cette approche fonctionne

* JWT standard et portable
* Transport via HTTP (cookies)
* Compatible REST, RPC REST et RPC XML
* Architecture micro-services réaliste

---

## 🎓 Phrase clé (rapport / soutenance)

> *Le JWT est transmis au niveau HTTP via des cookies, puis décodé dans chaque service, indépendamment du type de RPC utilisé.*

---

## ✅ Résumé

* Auth REST → génère JWT
* JWT stocké dans `access_token`
* Cookie partagé entre services
* Chaque service décode le token
* `user_id` + `role` contrôlent l’accès
* RPC XML et RPC REST peuvent coexister

