# PRD — Système d’Authentification Complet

**Stack demandée : Python + SQLite**
**Produit :** Landing Page + Login + Signup + Forgot Password + Reset Password + Dashboard

---

# 1. Vue d’Ensemble

Créer une application web complète avec :

* Landing page moderne
* Authentification sécurisée
* Création de compte
* Connexion utilisateur
* Mot de passe oublié
* Réinitialisation du mot de passe
* Dashboard privé
* Vérificateur de force du mot de passe
* Base de données SQLite
* Backend Python

---

# 2. Stack Technique

## Backend

* **Python 3.12+**
* **Flask**

## Frontend

* Tailwind

## Database

* SQLite (`database.db`)

## Sécurité

* bcrypt
* JWT ou Session Cookies
* CSRF Protection

---

# 3. Structure du Projet

```bash
project/
│── app.py
│── database.db
│── templates/
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   ├── forgot-password.html
│   ├── reset-password.html
│   └── dashboard.html
│
│── static/
│   ├── css/
│   └── js/
│
│── models.py
│── auth.py
│── utils.py
```

---

# 4. Pages à Créer

---

# 4.1 Landing Page

### Sections :

* Navbar
* Hero section
* Features
* Pricing
* Testimonials
* CTA
* Footer

### CTA Buttons :

* Login
* Create Account

---

# 4.2 Register Page

### Champs :

* Full Name
* Email
* Password
* Confirm Password

### Features :

* Password checker live
* Validation email unique

### Bouton :

* Create Account

---

# 4.3 Login Page

### Champs :

* Email
* Password

### Options :

* Remember me
* Show password

### Liens :

* Forgot Password
* Create Account

---

# 4.4 Forgot Password

### Champ :

* Email

### Bouton :

* Send Reset Link

---

# 4.5 Reset Password

### Champs :

* New Password
* Confirm Password

### Bouton :

* Reset Password

---

# 4.6 Dashboard

### Sidebar :

* Overview
* Profile
* Security
* Settings
* Logout

### Cards :

* Welcome user
* Last login
* Account status

---

# 5. Database SQLite Schema

## users table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## password_resets table

```sql
CREATE TABLE password_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    token TEXT NOT NULL,
    expires_at TIMESTAMP
);
```

---

# 6. Fonctionnalités Backend

## Auth

* Register user
* Login user
* Logout user
* Session handling

## Password

* Hash avec bcrypt
* Reset token unique
* Expiration token

## Security

* CSRF protection
* Email validation
* Rate limiting login

---

# 7. Password Checker Rules

### Mot de passe fort :

* Minimum 8 caractères
* Majuscule
* Minuscule
* Nombre
* Symbole

### Score :

* Weak
* Medium
* Strong

---

# 8. Routes Flask

```python
/
 /login
 /register
 /forgot-password
 /reset/<token>
 /dashboard
 /logout
```

---

# 9. User Flow

Landing
→ Register
→ Login
→ Dashboard

Forgot Password
→ Email
→ Reset Link
→ New Password
→ Login

---

# 10. UI Style

* Clean SaaS style
* White / Dark mode
* Rounded cards
* Blue gradient
* Responsive mobile

---

# 11. Bonus Features

* Google Login
* 2FA
* Email verification
* Admin dashboard
* Login history

---

# 12. Prompt for AI Builder

```text
Create a full authentication website using Python Flask + SQLite.

Pages:
Landing page
Register
Login
Forgot password
Reset password
Dashboard

Use modern UI, Tailwind CSS, responsive design.

Include:
bcrypt password hashing
session auth
SQLite database
password strength checker
secure forms
dashboard with sidebar

Production ready code.
```

---

# 13. Recommendation

Best stack for this project:

✅ Flask + SQLite + Tailwind
