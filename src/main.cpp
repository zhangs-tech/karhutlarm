#include <Adafruit_Sensor.h>
#include <Arduino.h>
#include <DHT_U.h>
#include <PubSubClient.h>
#include <WiFi.h>

// Pins
const uint8_t MQ2_PIN = 34; // ADC1 pin; ADC2 pins read 0 while WiFi is on
const uint8_t DHT_PIN = 13;

const uint8_t LED_R_PIN = 23;
const uint8_t LED_G_PIN = 22;
const uint8_t LED_B_PIN = 21;

const uint8_t BUZZER_PIN = 18;

// Config
const float GAS_THRESHOLD = 3830.0;
const float TEMP_HIGH_THRESHOLD = 50.0;
const float HUMIDITY_LOW_THRESHOLD = 40.0;
const unsigned int BUZZER_FREQ = 2000;

const char *WIFI_SSID = "Wokwi-GUEST";
const char *WIFI_PASSWORD = "";

// https://www.hivemq.com/demos/websocket-client/
const char *MQTT_SERVER = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char *MQTT_CLIENT_ID = "bingus-sic-6767420";
const char *MQTT_TOPIC = "bingus-sic-6767420/sensors";

DHT_Unified dht(DHT_PIN, DHT22);
WiFiClient wifi_client;
PubSubClient mqtt_client(wifi_client);

enum class Status { NORMAL, WARNING, DANGER };

Status get_status(float gas, float temp, float humidity) {
  bool smoke = gas > GAS_THRESHOLD;
  bool high_temp = temp > TEMP_HIGH_THRESHOLD;
  bool low_humidity = humidity < HUMIDITY_LOW_THRESHOLD;

  if (high_temp || (smoke && low_humidity)) {
    return Status::DANGER;
  } else if (smoke || low_humidity) {
    return Status::WARNING;
  } else {
    return Status::NORMAL;
  }
}

// The LED is common anode (COM wired to 3V3)
// so a pin is LOW to turn a color on.
void set_rgb(bool r, bool g, bool b) {
  digitalWrite(LED_R_PIN, !r);
  digitalWrite(LED_G_PIN, !g);
  digitalWrite(LED_B_PIN, !b);
}

void handle_rgb_led(Status status) {
  switch (status) {
  case Status::NORMAL:
    set_rgb(false, true, false);
    break;
  case Status::WARNING:
    set_rgb(true, true, false);
    break;
  case Status::DANGER:
    set_rgb(true, false, false);
    break;
  }
}

void handle_buzzer(Status status) {
  if (status == Status::DANGER) {
    tone(BUZZER_PIN, BUZZER_FREQ);
  } else {
    noTone(BUZZER_PIN);
  }
}

void setup() {
  Serial.begin(9600);

  pinMode(LED_R_PIN, OUTPUT);
  pinMode(LED_G_PIN, OUTPUT);
  pinMode(LED_B_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  dht.begin();

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  mqtt_client.setServer(MQTT_SERVER, MQTT_PORT);
}

// Tries to (re)connect without blocking the sensor loop for long.
void ensure_mqtt_connected() {
  static unsigned long last_attempt = 0;
  if (mqtt_client.connected() ||
      (last_attempt != 0 && millis() - last_attempt < 5000)) {
    return;
  }
  last_attempt = millis();

  IPAddress broker_ip;
  if (!WiFi.hostByName(MQTT_SERVER, broker_ip)) {
    Serial.printf("DNS lookup for %s failed\r\n", MQTT_SERVER);
    return;
  }
  Serial.printf("Connecting to %s (%s)...\r\n", MQTT_SERVER,
                broker_ip.toString().c_str());

  if (mqtt_client.connect(MQTT_CLIENT_ID)) {
    Serial.println("Connected to MQTT broker");
  } else {
    Serial.print("Failed to connect to MQTT broker, rc=");
    Serial.println(mqtt_client.state());
  }
}

void publish_reading(float gas, float temp, float humidity, Status status) {
  if (!mqtt_client.connected()) {
    return;
  }

  static const char *STATUS_NAMES[] = {"NORMAL", "WARNING", "DANGER"};
  char payload[128];
  snprintf(payload, sizeof(payload),
           "{\"gas\":%.2f,\"temp\":%.2f,\"humidity\":%.2f,\"status\":\"%s\"}",
           gas, temp, humidity, STATUS_NAMES[static_cast<int>(status)]);
  mqtt_client.publish(MQTT_TOPIC, payload);
}

void loop() {
  ensure_mqtt_connected();
  mqtt_client.loop();

  float gas = static_cast<float>(analogRead(MQ2_PIN));

  float temp = 0.0;
  float humidity = 0.0;

  sensors_event_t event;
  dht.temperature().getEvent(&event);
  if (!isnan(event.temperature)) {
    temp = event.temperature;
  }

  dht.humidity().getEvent(&event);
  if (!isnan(event.relative_humidity)) {
    humidity = event.relative_humidity;
  }

  Status status = get_status(gas, temp, humidity);

  handle_rgb_led(status);
  handle_buzzer(status);

  Serial.printf("Gas: %.2f, Temp: %.2f, Humidity: %.2f, Status: %d\r\n", gas,
                temp, humidity, static_cast<int>(status));
  publish_reading(gas, temp, humidity, status);

  delay(1000);
}
