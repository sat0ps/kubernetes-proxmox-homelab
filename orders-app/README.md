# Orders application

Minimal three-tier workload for the platform-modernization project.

## Components

- Frontend: static HTML/JavaScript served by nginx on port 8080.
- API: FastAPI on port 8000.
- Database: PostgreSQL using the official image.

The frontend proxies `/api/*` to the API, so the browser does not need a direct database or internal API address.

## Local validation

The password in `compose.yaml` is an explicitly local-development-only value, not a production credential.

```bash
docker compose up --build -d
curl http://localhost:8080/healthz
curl http://localhost:8080/api/healthz
curl http://localhost:8080/api/readyz
curl -X POST http://localhost:8080/api/orders \
  -H 'Content-Type: application/json' \
  -d '{"customer":"Demo Customer","item":"Platform Widget","quantity":2}'
curl http://localhost:8080/api/orders
curl http://localhost:8080/api/metrics
docker compose down -v
```

Production credentials must be injected at runtime and must never be built into an image.

## Images

```bash
docker build -t orders-api:local ./api
docker build -t orders-frontend:local ./frontend
```

Both application containers run as non-root users. PostgreSQL remains the upstream official image and is not custom-built.

## Scope boundary

This directory contains the workload and container packaging only. Helm, Kubernetes deployment, Flux and Azure configuration belong to later issues.
