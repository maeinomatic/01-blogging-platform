Backend Implementation Plan — FastAPI + SQLModel + PostgreSQL (local Docker)

Overview

This document describes the short-term plan to build a production-ready, developer-friendly backend for the Blogging Platform using FastAPI (async), SQLModel/SQLAlchemy, Alembic migrations, PostgreSQL in Docker, and JWT authentication. The focus is local Docker development parity; production differences (secrets, managed DB, horizontal scaling) are noted separately.

Goals

- Deliver a clean, testable FastAPI backend with: async DB layer, typed models (SQLModel), Alembic migrations, JWT auth, REST endpoints for posts/comments/users, OpenAPI docs, and health checks.
- Provide a frictionless developer onboarding (venv, Docker, migrations, tests). 
- Add CI (lint + tests + migration checks) and pre-commit tooling.

Architecture & Components

- FastAPI app (ASGI) — routers for auth, posts, comments, health.
- Persistence: SQLModel models + async SQLAlchemy engine (asyncpg driver).
- Migrations: Alembic wired to SQLModel.metadata for autogenerate.
- Auth: JWT access tokens + password hashing (passlib).
- Services/Repos: small service layer to separate business logic from request handlers.
- Docker Compose: postgres service + backend service (for local dev).
- Tests: pytest + pytest-asyncio + httpx for integration tests.

File / Feature Map (to create)

- server/main.py — FastAPI app & router registration
- server/core/config.py — Pydantic Settings (env-driven)
- server/core/db.py — async engine, sessionmaker, Base/metadata export
- server/core/security.py — JWT helpers, password hashing
- server/models/* — SQLModel definitions (User, Post, Comment, related indexes)
- server/api/* — routers (auth.py, posts.py, comments.py)
- server/services/* & server/repos/* — business logic and DB layers
- server/tests/* — unit + integration tests
- server/Dockerfile — multi-stage build for backend
- docker-compose.yml — add backend service (depends_on db)
- alembic/env.py — import SQLModel.metadata and set target_metadata
- alembic/versions/0001_init.py — initial migration
- .pre-commit-config.yaml, pyproject.toml — formatting & linting config
- .github/workflows/ci.yml — run lint, tests, migrations on PRs

Milestones & Timeline (suggested)

1. Core scaffold + DB wiring (1 day)
   - server core files, db session, Dockerfile, Compose backend service
   - set up config and `.env.example`
2. Models + migrations (1 day)
   - implement basic models (User, Post, Comment)
   - wire Alembic target_metadata and create initial migration
3. Auth + CRUD endpoints (1–2 days)
   - JWT auth, register/login, posts CRUD, comments create/read
4. Tests + docs (1 day)
   - unit + integration tests, OpenAPI improvements, README onboarding
5. CI + quality (1 day)
   - pre-commit, GitHub Actions, coverage threshold

Developer Onboarding (local Docker)

- Prerequisites:
  - Docker & Docker Compose
  - Python 3.10+ (venv recommended)
  - Node.js & npm (for frontend if you use the `client/` folder)

- Quick start (cloned repo):
  1. Copy env: `cp .env.example .env` and set strong `JWT_SECRET` and `POSTGRES_PASSWORD`.
  2. Start DB: `docker-compose up -d` (Postgres runs on `db:5432`, mapped to host by `.env`).
  3. Create + activate venv, install deps: `python -m venv .venv && . .venv/Scripts/Activate.ps1 && pip install -r requirements.txt` (Windows PowerShell example).
  4. Run Alembic migrations: `alembic upgrade head`.
  5. Start backend locally: `uvicorn server.main:app --reload`.
  6. (Optional) Start client: `cd client && npm install && npm start`.

Tests & Quality

- Run tests: `pytest` (integration tests will use the running Postgres DB).
- Lint & format: `black .`, `ruff .` — pre-commit will run these checks automatically.

CI / Release

- CI will run: install deps, run lint, run tests, run `alembic heads` / `alembic current` to ensure migrations are consistent.
- Release/build uses the Dockerfile and a registry (optional: GitHub Container Registry).

Production Notes (differences from local Docker dev)

- Use managed Postgres (RDS/Azure/Cloud SQL) and secure secrets (Vault, secrets manager, or environment variables provided by the platform).
- Configure proper number of Uvicorn workers behind a process manager (Gunicorn with Uvicorn workers or container orchestration with replicas).
- Add observability (structured logging, metrics, Sentry).
- Use separate migrations pipeline (CI or operator-triggered) and DB backups.

## Database schema (design)

This section defines the recommended PostgreSQL schema for the blogging platform — the canonical model to implement in SQLModel and commit as the first Alembic migration.

Core tables
- users — authentication and user profiles (UUID PK, email UNIQUE, password_hash, username UNIQUE, display_name, avatar_url, is_active, created_at, updated_at).
- posts — blog posts (UUID PK, author_id FK -> users, title, slug UNIQUE, status enum, published_at, summary, content_raw, content_html, content_json JSONB, metadata JSONB, search_vector tsvector, comments_count, likes_count, created_at, updated_at, deleted_at).
- comments — post comments and replies (UUID PK, post_id FK, author_id FK nullable, parent_id FK nullable, content, path/materialized_path or ltree, is_moderated, created_at, updated_at, deleted_at).
- tags / post_tags — many-to-many for post tagging (tags: id, name UNIQUE, slug; post_tags: post_id, tag_id PK composite).
- post_likes — user likes on posts (id, user_id FK, post_id FK, UNIQUE(user_id, post_id)).
- bookmarks — user saved posts (id, user_id FK, post_id FK, UNIQUE(user_id, post_id)).
- media — uploaded media/attachments (id, uploader_id FK, url, type, meta JSONB, created_at).
- refresh_tokens (or sessions) — token/session management (id, user_id, token_hash, user_agent, ip, expires_at, revoked, created_at).

Optional / recommended
- post_versions — store historical copies of posts for rollback/audit (post_id FK, version int, content_raw/content_html, metadata JSONB, created_at, author_id).
- post_views (analytics) — optional, used for view counts and analytics (post_id, user_id nullable, ip_hash, seen_at).

Indexes & constraints
- Use UUID primary keys for main entities.
- Unique constraints on `users.email`, `users.username`, `posts.slug` (global or scoped to author), `tags.name`.
- FK constraints for referential integrity and cascading behavior where appropriate (soft-delete is preferred for posts/comments).
- GIN index on `posts.search_vector` (tsvector) for fast full‑text search: `CREATE INDEX ON posts USING GIN(search_vector);`.
- GIN indexes on JSONB columns that are frequently queried (e.g., `metadata`).
- B-tree indexes on `posts.published_at`, `posts.author_id`, and `post_tags.post_id` for feed and lookup performance.

Full‑text search strategy
- Store a `search_vector` (tsvector) in `posts` combining title, summary, and content fields.
- Maintain `search_vector` via application update or a DB trigger on INSERT/UPDATE.
- Query with `to_tsquery`/`websearch_to_tsquery` and rank using `ts_rank_cd`. If search needs grow, introduce an external search engine (MeiliSearch/Elasticsearch) later.

Denormalization & counters
- Keep denormalized counters on `posts` (comments_count, likes_count, bookmarks_count) and update within transactions to avoid expensive COUNT(*) queries on read paths.

Comment threading policy
- Support reply threads via `parent_id` and optionally `path` (materialized path or Postgres `ltree`) to simplify retrieving nested threads. Limit nesting depth on UI if needed.

Migrations & dev workflow
- Implement models in `server/models/` (SQLModel) and wire `SQLModel.metadata` into `alembic/env.py` for autogenerate support.
- After models are implemented: `alembic revision --autogenerate -m "init"` then `alembic upgrade head`.
- Add SQL scripts or triggers (tsvector update) as part of migrations if using DB triggers.

MVP to implement immediately
- Implement tables: `users`, `posts`, `comments`, `tags`, `post_tags`, `post_likes`, `bookmarks`, `refresh_tokens` and `media`.
- Add `search_vector` + GIN index on `posts`.
- Add basic FK constraints, unique constraints on email/username/slug, and denormalized counters on `posts`.

Next steps
- Convert this schema to SQLModel classes and generate the initial Alembic migration.
- Decide on slug uniqueness policy (global vs per-author) and comment nesting strategy (parent-only vs ltree).
Next actions

- I will scaffold the server layout, wire Alembic to SQLModel metadata, add initial models and create the initial migration, plus update README onboarding. After that we will review and then design the database schema (tables/relations) together.

Questions / decisions required

- Confirm you want the SQLModel approach (Pydantic + ORM combined). (recommended)
- Confirm token policy: access tokens only or access+refresh token flow?

-- End of plan
