# Study Buddy Backend

## Current implementation

FastAPI backend for authenticated and guest study sessions, document ingestion, retrieval-grounded chat, and operational health checks.

### Architecture

- API layer: app/routers owns HTTP contracts, status codes, and request validation.
- Persistence: SQLAlchemy models in app/models; one request-scoped session per request.
- Services: app/services contains authentication, parsing, vector retrieval, and Groq integration.
- Configuration: Pydantic Settings reads environment variables; secrets are never logged.
- Storage: PostgreSQL for relational data, ChromaDB for embeddings, local filesystem for uploaded files.
- Tests: isolated SQLite database and mocked external AI/indexing boundaries.

The misspelled app/sevices package remains as thin compatibility shims. New code must import from app.services.

## Run locally

From the backend directory:

    ..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

OpenAPI docs: http://127.0.0.1:8000/docs

Health endpoints: GET /health/live and GET /health/ready. These currently report process health, not full dependency health.

## Environment

Copy .env.example to .env and configure values locally. Production requires SECRET_KEY, DATABASE_URL, and GROQ_API_KEY. The local fallback signing key is unsafe and must never be used in production. The existing local .env should use the exact key name SECRET_KEY; a misspelled SCRET_KEY is ignored. Never put secret values in logs or documentation.

## API workflow

1. POST /api/auth/register with email/password.
2. POST /api/auth/login and retain the bearer token.
3. Or POST /api/auth/guest for a guest session and its session-scoped bearer token.
4. POST /api/upload multipart form with file; optional session_id for authenticated users. Guest tokens are bound to their created session.
5. POST /api/chat/{session_id}/messages with JSON message and optional action (teach, keypoints, quiz, examtips). Response uses Server-Sent Events.
6. GET /api/sessions lists sessions available to the identity.
7. DELETE /api/upload/{file_id} deletes an owned document.

Supported extensions: PDF, DOCX, PPTX, JPG/JPEG, PNG, TXT. Legacy binary DOC/PPT are rejected because configured parsers do not support them safely.

## Tests

Run from backend:

    ..\.venv\Scripts\python.exe -m unittest discover -s tests -v

Tests use in-memory SQLite and mock expensive/external indexing. They cover registration/login, duplicate accounts, invalid credentials, guest tokens, cross-identity access, protected routes, invalid/empty uploads, successful upload, and chat preconditions.

## Reliability and security notes

- SQLAlchemy uses connection pre-ping and connection recycling.
- Passwords are hashed; bearer tokens are signed and expire.
- Ownership failures return 404 to avoid disclosing another user's session.
- Uploads have a bounded read size, sanitized basename, random stored filename, and processing rollback.
- Parsing and embedding calls run outside the async event loop.
- Groq SDK retries are configured; provider failures return generic client-safe messages and are logged server-side.
- ChromaDB and embedding models are lazy-loaded.
- No database schema is auto-created at startup. Use reviewed Alembic migrations before deployment.
- Do not deploy with local disk uploads or one local Chroma directory across multiple app replicas. Production needs shared object storage, managed vector storage, background jobs, and backups.
- Interrupted streaming may leave a user message without an assistant reply; production should add message states and idempotency keys.

## Production hardening still required

This is a functional baseline, not production certification. Before real traffic:

- Add Alembic migrations and validate them against staging first.
- Add rate limits, email verification, password reset, token revocation, audit events, and abuse controls.
- Validate file signatures and malware-scan uploads; defend against decompression bombs.
- Move parsing/indexing to a durable worker queue with retries, dead-letter handling, and job status polling.
- Add storage abstraction, encryption at rest, retention/deletion policy, backups, restore drills, and orphan reconciliation.
- Add metrics, tracing, structured redacted logs, alerting, provider circuit breaker, and dependency-specific readiness checks.
- Run load, soak, concurrency, chaos, and recovery tests using production-like infrastructure.

## Local configuration security check

The local environment file previously used the misspelled key SCRET_KEY. It has been renamed to SECRET_KEY without displaying or changing its value. The value is shorter than the recommended 32 characters; replace it with a newly generated random secret before using the app outside local development. Rotate it before deployment because any tokens signed with the old key will no longer validate after rotation.


## Database migrations

The initial Alembic revision is in migrations/versions/0001_initial.py. Review migration SQL before applying it. From backend, generate SQL without connecting using:

    $env:DATABASE_URL = "postgresql://user:password@localhost/studybuddy"
    ..\.venv\Scripts\python.exe -m alembic upgrade head --sql

Apply to a deliberately selected database only after backup and staging validation:

    ..\.venv\Scripts\python.exe -m alembic upgrade head

Never run upgrade or downgrade against a database without confirming the target and backup first.
