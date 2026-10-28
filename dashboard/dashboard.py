"""Karhutla dashboard: subscribe to the ESP32 MQTT topic and plot readings.

Run:   python dashboard/dashboard.py
Open:  dashboard/dashboard.html (auto-refreshes every 2 seconds)
Stop:  Ctrl+C (the HTML file is written one last time)
"""

import json
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Must match src/main.cpp
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "bingus-sic-6767420/sensors"

GAS_THRESHOLD = 3830
TEMP_HIGH_THRESHOLD = 50.0
HUMIDITY_LOW_THRESHOLD = 40.0

MAX_POINTS = 300
REFRESH_SECONDS = 2
OUTPUT = Path(__file__).with_name("dashboard.html")

STATUS_COLORS = {"NORMAL": "#2e9e4f", "WARNING": "#e6b800", "DANGER": "#d62828"}

lock = threading.Lock()
times = deque(maxlen=MAX_POINTS)
gas = deque(maxlen=MAX_POINTS)
temp = deque(maxlen=MAX_POINTS)
humidity = deque(maxlen=MAX_POINTS)
status = deque(maxlen=MAX_POINTS)
alerts = deque(maxlen=10)  # status changes, newest last


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"MQTT connect failed: {reason_code}")
        return
    print(f"Connected to {BROKER}:{PORT}, subscribing to {TOPIC}")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        row = (
            float(data["gas"]),
            float(data["temp"]),
            float(data["humidity"]),
            str(data["status"]),
        )
    except (ValueError, KeyError, TypeError) as err:
        print(f"Ignoring bad payload {msg.payload!r}: {err}")
        return

    now = datetime.now()
    with lock:
        if not status or status[-1] != row[3]:
            alerts.append(f"{now:%H:%M:%S}  {row[3]}")
        times.append(now)
        gas.append(row[0])
        temp.append(row[1])
        humidity.append(row[2])
        status.append(row[3])
    print(f"{now:%H:%M:%S} gas={row[0]:.0f} temp={row[1]:.1f} "
          f"hum={row[2]:.1f} status={row[3]}")


def build_html():
    with lock:
        t, g, tp, h, s = (list(x) for x in (times, gas, temp, humidity, status))
        recent_alerts = list(alerts)

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.07,
        subplot_titles=("Gas (MQ-2, raw ADC)", "Temperature (C)", "Humidity (%)"),
    )
    fig.add_trace(go.Scatter(x=t, y=g, name="Gas", line=dict(color="#6a4c93")), 1, 1)
    fig.add_hline(y=GAS_THRESHOLD, line_dash="dash", line_color="red", row=1, col=1)
    fig.add_trace(go.Scatter(x=t, y=tp, name="Temp", line=dict(color="#e76f51")), 2, 1)
    fig.add_hline(y=TEMP_HIGH_THRESHOLD, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_trace(go.Scatter(x=t, y=h, name="Humidity", line=dict(color="#1d7fb8")), 3, 1)
    fig.add_hline(y=HUMIDITY_LOW_THRESHOLD, line_dash="dash", line_color="red", row=3, col=1)

    # Mark each point with its status color on the gas chart.
    fig.add_trace(
        go.Scatter(
            x=t, y=g, mode="markers", name="Status", showlegend=False,
            marker=dict(color=[STATUS_COLORS.get(x, "gray") for x in s], size=6),
            text=s, hovertemplate="%{text}<extra></extra>",
        ),
        1, 1,
    )
    fig.update_layout(height=760, margin=dict(t=40, b=30), showlegend=False)

    current = s[-1] if s else "NO DATA"
    color = STATUS_COLORS.get(current, "gray")
    latest = (
        f"Gas {g[-1]:.0f} | Temp {tp[-1]:.1f} C | Humidity {h[-1]:.1f} %"
        if s else "Waiting for data from the ESP32..."
    )
    alert_items = "".join(f"<li>{a}</li>" for a in reversed(recent_alerts)) or "<li>None</li>"

    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="{REFRESH_SECONDS}">
<title>Karhutla Dashboard</title>
<style>
 body {{ font-family: sans-serif; margin: 16px; }}
 .badge {{ display:inline-block; padding:10px 24px; border-radius:8px;
          color:#fff; font-size:28px; font-weight:bold; background:{color}; }}
 .row {{ display:flex; gap:32px; align-items:flex-start; flex-wrap:wrap; }}
</style></head><body>
<h2>Karhutla IoT Monitoring and Warning</h2>
<div class="row">
  <div><div class="badge">{current}</div><p>{latest}</p></div>
  <div><b>Status changes</b><ul>{alert_items}</ul></div>
</div>
{fig.to_html(full_html=False, include_plotlyjs="cdn")}
</body></html>"""


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()
    print(f"Writing {OUTPUT} every {REFRESH_SECONDS}s. Ctrl+C to stop.")
    try:
        while True:
            OUTPUT.write_text(build_html(), encoding="utf-8")
            time.sleep(REFRESH_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()
        OUTPUT.write_text(build_html(), encoding="utf-8")
        print("Stopped.")


if __name__ == "__main__":
    main()
