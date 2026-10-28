# Karhutla IoT Monitoring and Warning

## Wokwi Web Setup

Simply copy these files to wokwi:

- `diagram.json`
- `libraries.txt`
- `src/main.cpp`

## MQTT

- Server: `broker.hivemq.com`
- Topic: `bingus-sic-6767420/sensors`

## Python Dashboard

The dashboard subscribes to the MQTT topic above and writes `dashboard/dashboard.html`
with the current status, the latest values, and trend charts (Plotly).
Start the Wokwi simulation first, then run the dashboard from the project root.

### With uv

```
uv venv
uv pip install -r dashboard/requirements.txt
uv run python dashboard/dashboard.py
```

### With pip

```
python -m venv .venv
.venv\Scripts\activate
pip install -r dashboard/requirements.txt
python dashboard/dashboard.py
```

On macOS or Linux, replace the activate line with `source .venv/bin/activate`.

Open `dashboard/dashboard.html` in a browser. It refreshes every 2 seconds.
Press Ctrl+C to stop the dashboard.
