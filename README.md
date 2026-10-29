# Karhutla IoT Monitoring and Warning

## Wokwi Web Setup

Links: https://wokwi.com/projects/479191049079829505

Or just simply copy these files to wokwi:

- `diagram.json`
- `libraries.txt`
- `src/main.cpp`

## MQTT

- Server: `broker.hivemq.com`
- Topic: `bingus-sic-6767420/sensors`

## Dashboard

A FastAPI backend (`dashboard/src/dashboard/`) subscribes to the MQTT topic above,
stores every reading in SQLite (`dashboard/karhutla.db`), and serves a JSON API.
The frontend (`dashboard/web/`) polls that API and updates the charts in place.
Start the Wokwi simulation first, then run:

```
cd dashboard
uv run fastapi dev     # auto-reload, for development
uv run fastapi run     # or without reload
```

Open http://127.0.0.1:8000 in a browser. API docs are at http://127.0.0.1:8000/docs.

### API

- `GET /api/readings?limit=300`: the latest readings, oldest first
- `GET /api/readings?after_id=<id>`: readings newer than `id` (used for polling)
- `GET /api/thresholds`: alert thresholds, drawn as dashed lines on the charts

### Configuration

Settings can be overridden with `DASHBOARD_*` environment variables or a
`dashboard/.env` file, e.g. `DASHBOARD_MQTT_TOPIC`, `DASHBOARD_DB_PATH`.
See `dashboard/src/dashboard/config.py` for the full list.
