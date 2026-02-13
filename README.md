you said # Blogging Platform

A full-stack blogging application with user authentication, rich text editor, comments, and search functionality.

## Features

- User Authentication (JWT)
- Create, Read, Update, Delete blog posts
- Rich text editor (TinyMCE/Slate)
- Comments system
- Search and filtering
- User profiles
- Like/bookmark posts

## Tech Stack

- **Frontend:** React, Tailwind CSS
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL (Postgres in Docker for local development)
- **Authentication:** JWT
- **Editor:** React-Quill or TinyMCE

## Project Structure

```
├── client/              # React frontend
├── server/              # FastAPI backend
├── README.md
└── requirements.txt     # Python dependencies
```

## Getting Started

See `ONBOARDING.md` for complete, platform-specific developer onboarding (venv, Docker, migrations, helper scripts, and troubleshooting).

Quick links:
- Start backend (dev): `uvicorn server.main:app --reload`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

For full step‑by‑step commands and troubleshooting, open `ONBOARDING.md`.

## API Endpoints
- If `docker-compose up -d` fails, run `docker-compose logs db` to see startup errors or the healthcheck output.

## API Endpoints

- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login user
- `GET /api/posts` - Get all posts
- `POST /api/posts` - Create post
- `GET /api/posts/:id` - Get single post
- `PUT /api/posts/:id` - Update post
- `DELETE /api/posts/:id` - Delete post
- `POST /api/posts/:id/comments` - Add comment

## Database (chosen)

We use **PostgreSQL** for this project (local development runs Postgres inside Docker). Postgres gives transactional integrity, mature tooling, and JSONB when semi-structured storage is useful — it fits a production blogging platform and is a good match for SQLModel/SQLAlchemy + Alembic migrations.

Why Postgres
- ACID-compliant and reliable for user data and transactions.
- Powerful SQL, indexing and full-text search options for a blog.
- JSONB support if you need flexible metadata per post.
- Excellent ecosystem (pgAdmin, extensions, cloud providers).

Local developer setup
- The repository includes `docker-compose.yml` that runs `postgres:15` for local development. Use `DATABASE_URL` from `.env` to point your backend at the running container (`db` host from inside Docker or `localhost` from host).

Migration strategy
- Use Alembic (already configured) for versioned schema changes; autogenerate migrations from SQLModel models and apply with `alembic upgrade head`.

## License

MIT
