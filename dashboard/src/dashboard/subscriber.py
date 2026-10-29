import json
import logging

import paho.mqtt.client as mqtt

from .config import Settings
from .db import ReadingStore

log = logging.getLogger(__name__)

STATUSES = {"NORMAL", "WARNING", "DANGER"}


def start_subscriber(store: ReadingStore, settings: Settings) -> mqtt.Client:
    """Connect in the background; paho reconnects on its own if the link drops."""

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            log.warning("MQTT connect failed: %s", reason_code)
            return
        log.info("Connected to %s:%s, subscribing to %s",
                 settings.mqtt_broker, settings.mqtt_port, settings.mqtt_topic)
        client.subscribe(settings.mqtt_topic)

    def on_message(client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            gas = float(data["gas"])
            temp = float(data["temp"])
            humidity = float(data["humidity"])
            status = str(data["status"])
            if status not in STATUSES:
                raise ValueError(f"unknown status {status!r}")
        except (ValueError, KeyError, TypeError) as err:
            log.warning("Ignoring bad payload %r: %s", msg.payload, err)
            return
        store.add(gas, temp, humidity, status)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect_async(settings.mqtt_broker, settings.mqtt_port, keepalive=60)
    client.loop_start()
    return client
