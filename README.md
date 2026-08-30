# FastAPI Backend

A FastAPI backend built with a layered (clean) architecture: controllers → use cases → repositories, backed by MongoDB Atlas (via Motor) and Upstash Redis. Includes JWT-based auth, rate limiting, and idempotency protection as ASGI middleware.

## Tech Stack

- **Framework:** FastAPI (ASGI, async throughout)
- **Server:** Uvicorn
- **Database:** MongoDB Atlas, accessed via Motor (`AsyncIOMotorClient`)
- **Cache / Rate limiting / Sessions:** Upstash Redis (REST-based async client)
- **Auth:** JWT (`pyjwt`) + `bcrypt` password hashing
- **Testing:** `pytest` + `pytest-asyncio` + `httpx` (in-memory ASGI test client, no real DB/Redis required)
- **Containerization:** Docker + Docker Compose

## Architecture

The codebase follows a layered structure so business logic stays independent of FastAPI, MongoDB, and Redis:

```
src/
├── domain/
│   └── models.py                  # Plain domain entities (User, Pitch, etc.)
├── application/
│   ├── dtos/                      # @dataclass request/response DTOs
│   ├── interfaces/
│   │   ├── repository.py          # Abstract repository interfaces (ABCs)
│   │   └── use_case/              # Use cases (business logic, no framework imports)
│   └── exceptions.py              # Domain-level exceptions
├── infrastructure/
│   ├── database/                  # Mongo client + repository implementations
│   ├── config/                    # Redis client (Upstash)
│   └── web/
│       ├── controllers/           # Thin FastAPI-facing controllers
│       ├── Routers/                # APIRouter wiring
│       ├── middleware/            # Auth, rate limiting, idempotency
│       └── dependencies.py        # Dependency-injection factories
tests/
├── conftest.py                    # Shared fixtures, fake repos wired via dependency_overrides
├── test_repository/                # Fake in-memory repositories for testing
├── test_auth_controller.py
└── test_pitch_controller.py
main.py                            # App entrypoint, lifespan, middleware/router wiring
```

**Request flow:** `Router → Controller → Use Case → Repository Interface → Repository Implementation → MongoDB`

Each layer only depends on the layer directly below it. Use cases depend on abstract repository interfaces, not concrete MongoDB implementations — this is what allows the test suite to swap in fake, in-memory repositories with zero real database calls.

## Prerequisites

- Python 3.12+
- Docker Desktop (for containerized run)
- A MongoDB Atlas cluster (or a local `mongo` container for development)
- An Upstash Redis database

## Environment Variables

Create a `.env` file in the project root:

```bash
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net
MONGO_DB_NAME=leadsengineops
JWT_SECRET_KEY=<a-long-random-secret>
UPSTASH_REDIS_REST_URL=https://<your-upstash-url>
UPSTASH_REDIS_REST_TOKEN=<your-upstash-token>
```

`.env` is git-ignored and never baked into the Docker image — only loaded at container runtime via `env_file` in `docker-compose.yml`.

## Running Locally (without Docker)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

App runs at `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.

## Running with Docker

```bash
docker compose up --build
```

This builds the image from the `Dockerfile`, starts the `api` service, and mounts the project directory as a volume so code changes hot-reload without rebuilding.

Stop with:

```bash
docker compose down
```

### Using a local MongoDB instead of Atlas (development)

For local development without depending on Atlas connectivity, add a `mongo` service to `docker-compose.yml` and point `MONGO_URI` at it (`mongodb://mongo:27017`) instead of the Atlas connection string. Switch back to the real Atlas URI before deploying.

## API Overview

| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Create a new user account |
| POST | `/auth/login` | Authenticate, returns a JWT access token |
| GET | `/protected/pitch/me` | Get the authenticated user's pitch (requires `Authorization: Bearer <token>`) |

Full interactive documentation (Swagger UI) is available at `/docs` once the app is running.

## Middleware

Applied in `main.py` via `setup_middleware(app)`:

- **AuthMiddleware** — validates the `Authorization: Bearer <token>` header, checks JWT validity and session activity (sliding 15-minute inactivity timeout backed by Redis), sets `request.state.current_user`.
- **RateLimiterMiddleware** — escalating token-bucket rate limiting per user/IP, backed by Redis, with increasing lockout durations on repeated violations.
- **IdempotencyManager** (per-route dependency, not global middleware) — protects mutating (`POST`/`PUT`/`PATCH`) endpoints against duplicate submissions using an `X-Idempotency-Key` header.

All middleware is skipped when `ENV=test` so the test suite can exercise controllers/use cases in isolation.

## Testing

The test suite runs entirely **in-memory** — no real MongoDB, no real Redis, no network calls. This is achieved by:

1. Setting `ENV=test`, which disables `AuthMiddleware`/`RateLimiterMiddleware` and skips the real Mongo/Redis connection verification in `main.py`'s lifespan.
2. Overriding FastAPI's dependency-injection functions (`app.dependency_overrides`) so use cases receive fake, in-memory repository implementations instead of the real MongoDB-backed ones.

### Running tests

**Inside Docker (recommended — matches the environment pytest is installed in):**

```bash
docker compose run --rm api pytest tests/ -v
```

**Locally (if `pytest` is installed on your host machine):**

```bash
pip install pytest pytest-asyncio httpx
python -m pytest tests/ -v
```

### Test structure

- `tests/conftest.py` — defines the `client` fixture (an in-memory `httpx.AsyncClient` wired to the FastAPI app via `ASGITransport`), plus `fake_user_repo` / `fake_pitch_repo` fixtures. Overrides real dependency factories with fakes for the duration of each test.
- `tests/test_repository/` — fake, in-memory implementations of the repository interfaces (`FakeUserRepository`, `FakePitchRepository`), each implementing every abstract method declared on its corresponding `Abstract*Repository` interface, plus a `seed()` helper for pre-populating test data.
- `tests/test_auth_controller.py` — login success, wrong password, user-not-found cases.
- `tests/test_pitch_controller.py` — pitch retrieval success and not-found cases.

### Writing new tests

1. Add any new fake repository methods needed to the relevant fake in `tests/test_repository/`, matching the exact method signatures declared on the real `Abstract*Repository` interface (Python's `ABC` will refuse to instantiate a fake that's missing any abstract method).
2. Use `client`, `fake_user_repo`, `fake_pitch_repo` as test function parameters — **do not import them** from `conftest.py`; pytest auto-injects fixtures from `conftest.py` into any test in the same directory tree.
3. Seed fake data via the fake repository's `seed()` helper before making a request through `client`.

## Project Conventions

- **DTOs** (`@dataclass`) carry data between the controller and use case layers — they never include sensitive fields like password hashes.
- **Domain entities** (e.g. `User`) carry the full internal representation, including hashed passwords — used only within use cases and repositories, never returned directly in an API response.
- **Exceptions** are defined once in `src/application/exceptions.py` and mapped to HTTP status codes at the controller layer (e.g. `UserAlreadyExistsError` → `409`, `PitchNotFoundError` → `404`).
- **Repository interfaces** (`Abstract*Repository`) live in `src/application/interfaces/`; concrete MongoDB implementations live in `src/infrastructure/database/`. Use cases only ever depend on the interface.
