# Flask Auth Site

Production-ready authentication site using Flask, SQLite, JWT cookies, CSRF protection, bcrypt, SMTP password reset, and Tailwind CSS.

## Quick start

1. Create a virtual environment and install Python deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Install Tailwind and build CSS:

```bash
npm install
npm run build:css
```

3. Configure environment variables:

```bash
cp .env.example .env
```

4. Run the app:

```bash
python app.py
```

## Routes

- `/` Landing
- `/register`
- `/login`
- `/forgot-password`
- `/reset/<token>`
- `/dashboard`
- `/logout`
