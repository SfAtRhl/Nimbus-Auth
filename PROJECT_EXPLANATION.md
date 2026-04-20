# Project explanation and security map

This project is a Flask-based authentication site with a landing page, full auth flow, and a JSON API. It uses SQLite for storage, JWT for sessions, bcrypt for password hashing, and CSRF protection for form posts.

## Project location

- Workspace root: this folder; entry point is [app.py](app.py)
- High-level setup and run steps: [README.md](README.md)

## Core layout and responsibilities

- App factory, config, request lifecycle hooks, and blueprint registration: [app.py](app.py#L11-L95)
- Web routes and HTML auth flow: [auth.py](auth.py#L24-L106)
- JSON API routes: [api.py](api.py#L23-L143)
- Database access and schema creation: [models.py](models.py#L5-L89)
- Security utilities (JWT, bcrypt, headers, guards): [utils.py](utils.py#L11-L117)
- Form validation rules: [forms.py](forms.py#L1-L46)
- CSRF and rate limiting extensions: [extensions.py](extensions.py#L1-L6)
- Templates for the UI: [templates/](templates/)
- Static JS helpers (theme toggle, password strength UI): [static/js/](static/js/)
- Translation strings for multilingual UI: [translations.py](translations.py)

## How the app boots

1. `create_app()` loads environment settings and configures the app, including JWT settings, cookie options, and rate limits. See [app.py](app.py#L11-L31).
2. CSRF and rate limiting extensions are attached to the app. See [app.py](app.py#L34-L35) and [extensions.py](extensions.py#L1-L6).
3. `before_request` loads the current user from the JWT cookie or header, and it also sets the active language and text direction. See [app.py](app.py#L39-L50) and [utils.py](utils.py#L67-L94).
4. `after_request` adds security headers to every response. See [app.py](app.py#L52-L57) and [utils.py](utils.py#L112-L117).
5. Database tables are created (if missing) on startup. See [app.py](app.py#L92-L93) and [models.py](models.py#L16-L40).

## Data model (SQLite)

- `users` table stores full name, email, bcrypt hash, and timestamps. See [models.py](models.py#L16-L28).
- `password_resets` table stores reset tokens and expiry times. See [models.py](models.py#L30-L38).

## Web UI flow (templates + routes)

- Landing page: [templates/landing.html](templates/landing.html) rendered by [app.py](app.py#L77-L79).
- Register: [auth.py](auth.py#L24-L32) and [templates/register.html](templates/register.html).
- Login: [auth.py](auth.py#L34-L58) and [templates/login.html](templates/login.html).
- Forgot password: [auth.py](auth.py#L60-L73) and [templates/forgot-password.html](templates/forgot-password.html).
- Reset password: [auth.py](auth.py#L75-L94) and [templates/reset-password.html](templates/reset-password.html).
- Dashboard (protected): [auth.py](auth.py#L96-L99) and [templates/dashboard.html](templates/dashboard.html).

## JSON API flow

- Register: [api.py](api.py#L40-L65)
- Login: [api.py](api.py#L67-L84)
- Current user: [api.py](api.py#L92-L97)
- Forgot password: [api.py](api.py#L99-L113)
- Reset password: [api.py](api.py#L115-L143)

## Security features (what, example, location)

### 1) bcrypt password hashing

- What it does: Passwords are never stored in plain text. They are hashed using bcrypt before being saved and verified on login.
- Example in code: `hash_password()` and `verify_password()` wrap bcrypt calls. See [utils.py](utils.py#L18-L22).
- Where it is used:
  - Web register and login: [auth.py](auth.py#L24-L56)
  - API register and login: [api.py](api.py#L40-L84)

### 2) JWT expiration and signature validation

- What it does: JWTs are created with an expiration time and signed with a server secret. On each request, the token is decoded and validated before loading the user.
- Example in code:
  - JWT creation and expiration fields (`exp`, `iat`): [utils.py](utils.py#L48-L62)
  - JWT decoding with signature and expiration validation: [utils.py](utils.py#L64-L80)
  - User loading from token: [utils.py](utils.py#L73-L94)
- Where it is configured:
  - Secrets and expiration config: [app.py](app.py#L17-L20)
- Where it is used:
  - Cookie set after login (HttpOnly, SameSite): [auth.py](auth.py#L43-L56)
  - JWT-based auth for API: [api.py](api.py#L92-L97)

### 3) CSRF protection on forms

- What it does: CSRF tokens are embedded in each form, and Flask-WTF verifies them on POST requests.
- Example in code:
  - CSRF extension setup: [extensions.py](extensions.py#L1-L6) and [app.py](app.py#L34-L35)
  - Hidden CSRF field on forms: [templates/login.html](templates/login.html#L20-L22) (same pattern in register/forgot/reset templates)

### 4) Login rate limiting

- What it does: Limits the number of login attempts per IP and email combination to reduce brute force attacks.
- Example in code:
  - Rate limiter init: [extensions.py](extensions.py#L1-L6)
  - Configurable limit value: [app.py](app.py#L28-L28)
  - Web login limit: [auth.py](auth.py#L34-L36)
  - API login limit: [api.py](api.py#L67-L69)

### 5) Security headers on responses

- What it does: Adds baseline security headers like `X-Frame-Options` and `X-Content-Type-Options` to every response.
- Example in code:
  - Header definitions: [utils.py](utils.py#L112-L117)
  - Applied after each request: [app.py](app.py#L52-L57)

## Password strength UX (frontend + backend)

- Frontend meter + rules UI: [static/js/password_strength.js](static/js/password_strength.js#L1-L46) and data attributes in [templates/register.html](templates/register.html#L20-L57) and [templates/reset-password.html](templates/reset-password.html#L7-L44).
- Backend rules and validation (server-side): [utils.py](utils.py#L24-L46) and [forms.py](forms.py#L8-L46).

## Localization and UI behavior

- Translation strings for English, French, Arabic: [translations.py](translations.py)
- Language selection stored in a cookie and exposed to templates: [app.py](app.py#L39-L75)
- Theme toggle and password show/hide: [static/js/app.js](static/js/app.js#L1-L59)

## End-to-end example (web login)

1. User submits login form with CSRF token. See [templates/login.html](templates/login.html#L20-L68).
2. Rate limiter checks the request. See [auth.py](auth.py#L34-L36).
3. Password is verified using bcrypt. See [auth.py](auth.py#L38-L41) and [utils.py](utils.py#L21-L22).
4. JWT is created with expiration and signed. See [auth.py](auth.py#L43-L56) and [utils.py](utils.py#L48-L62).
5. Response includes security headers and HttpOnly cookie. See [app.py](app.py#L52-L57) and [auth.py](auth.py#L49-L55).
6. Subsequent requests load the user from the JWT. See [app.py](app.py#L39-L42) and [utils.py](utils.py#L73-L94).
