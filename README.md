# InfraBox

Lightweight infrastructure inventory app backed by JSON files.

## Quick start

```bash
cp .env.example .env          # set SECRET_KEY before production
docker compose up -d --build
```

Open http://localhost:5043 — on first run you will be asked to create an admin account.

## Data

All application data lives in `data/*.json` and is **not** tracked in git. The `data/` directory is created automatically on startup; empty entity files are initialized as `[]`.

To persist data in Docker, `docker-compose.yml` mounts `./data` into the container.

## Local development

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Set `ENVCONFIG=DEV` in `.env` for debug mode (default when unset).

## Import / export

Use **Import / Export** in the UI to load or back up data:

- Full `.ibxf` backup (infra entities)
- Per-entity JSON import/export
- NetBox CSV import

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | — | Flask session secret (required in production) |
| `DATA_DIR` | `data` | Path to JSON data directory |
| `APP_NAME` | `InfraBox` | Display name |
| `ENVCONFIG` | `DEV` | `PROD` for production settings |
