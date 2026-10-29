# Karhutla Dashboard

Web dashboard for the ESP32 sensor readings. The FastAPI backend (`src/dashboard/`)
subscribes to the MQTT topic, stores every reading in SQLite (`karhutla.db`), and
serves the frontend (`web/`) along with a JSON API.

## Running

Start the Wokwi simulation (or the real ESP32) first so there is data to show.
Run all commands from this `dashboard/` directory.

### With uv

```
uv run fastapi dev
```

`uv run fastapi run` to run without reloading.

### With pip

```
python -m venv .venv
.venv\Scripts\activate
pip install -e .
fastapi dev
```

On macOS or Linux, replace the activate line with `source .venv/bin/activate`.

### Open the dashboard

- Dashboard: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

Press Ctrl+C to stop the server. Readings are kept in `karhutla.db`, so the
charts still show the history after a restart.

To open the dashboard from another device on the same network, use
`fastapi dev --host 0.0.0.0` and browse to this machine's IP address.

## Configuration

Every field in `src/dashboard/config.py` can be overridden with an environment
variable prefixed with `DASHBOARD_`, or in a `.env` file in this directory.
Start from the template, which lists every setting with its default:

```
cp .env.example .env
```

The MQTT settings and alert thresholds must match `src/main.cpp` in the firmware.

## API

- `GET /api/readings?limit=300`: the latest readings, oldest first
- `GET /api/readings?after_id=<id>`: readings newer than `id`, used for polling
- `GET /api/thresholds`: alert thresholds, drawn as dashed lines on the charts
