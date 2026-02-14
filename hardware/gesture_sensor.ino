/*
  ESP32 Gesture Sensor
  Reads gesture data and communicates with main computer
*/

/*
  ESP32 Gesture Sensor
  Reads gesture data from an APDS-9960 and sends simple strings
  over USB serial to the host. Uses the SparkFun APDS-9960 library.

  Install: Library Manager -> SparkFun APDS-9960 Arduino Library
  Wire: SDA -> GPIO21, SCL -> GPIO22 (typical ESP32)
*/

#include <Wire.h>
#include <SparkFun_APDS9960.h>

SparkFun_APDS9960 apds;

void setup() {
  Serial.begin(115200);
  delay(50);
  Wire.begin(21, 22); // SDA, SCL for ESP32
  if (!apds.init()) {
/*
  ESP32 Gesture Sensor (Serial + MQTT)
  Reads gesture data from an APDS-9960 and sends simple strings
  over USB serial and optionally publishes to an MQTT broker.

  Libraries required:
    - SparkFun APDS-9960
    - PubSubClient (for MQTT)

  Wire: SDA -> GPIO21, SCL -> GPIO22 (typical ESP32)

  Configure WiFi/MQTT by editing WIFI_SSID, WIFI_PASS, MQTT_SERVER, etc.
  To disable MQTT, set MQTT_ENABLED to false.
*/

#include <Wire.h>
#include <SparkFun_APDS9960.h>
#include <WiFi.h>
#include <PubSubClient.h>

// === CONFIGURE ===
const char* WIFI_SSID = "YOUR_SSID";
const char* WIFI_PASS = "YOUR_PASSWORD";
const char* MQTT_SERVER = "192.168.1.10"; // broker IP or hostname
const uint16_t MQTT_PORT = 1883;
const char* MQTT_TOPIC = "holomed/gesture";
const bool MQTT_ENABLED = true;
// =================

SparkFun_APDS9960 apds;
WiFiClient espClient;
PubSubClient mqttClient(espClient);

void mqttReconnect() {
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32-Gesture-" + String((uint32_t)ESP.getEfuseMac(), HEX);
    if (mqttClient.connect(clientId.c_str())) {
      Serial.println("connected");
      mqttClient.subscribe(MQTT_TOPIC);
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 2 seconds");
      delay(2000);
    }
  }
}

void publishGesture(const char* msg) {
  Serial.println(msg);
  if (MQTT_ENABLED && mqttClient.connected()) {
    mqttClient.publish(MQTT_TOPIC, msg);
  }
}

void setup() {
  Serial.begin(115200);
  delay(50);
  Wire.begin(21, 22); // SDA, SCL for ESP32
  if (!apds.init()) {
    Serial.println("APDS-9960 init failed");
    while (1) delay(1000);
  }
  if (!apds.enableGestureSensor(true)) {
    Serial.println("Failed to enable gesture sensor");
    while (1) delay(1000);
  }

  if (MQTT_ENABLED) {
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("Connecting to WiFi");
    uint8_t tcount = 0;
    while (WiFi.status() != WL_CONNECTED && tcount < 60) {
      delay(500);
      Serial.print('.');
      tcount++;
    }
    Serial.println();
    if (WiFi.status() == WL_CONNECTED) {
      Serial.print("WiFi connected, IP: ");
      Serial.println(WiFi.localIP());
      mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
    } else {
      Serial.println("WiFi connection failed - MQTT disabled");
    }
  }

  Serial.println("ESP32 Gesture Sensor Initialized");
}

void loop() {
  if (MQTT_ENABLED) {
    if (!mqttClient.connected()) mqttReconnect();
    mqttClient.loop();
  }

  if (apds.isGestureAvailable()) {
    int gesture = apds.readGesture();
    switch (gesture) {
      case DIR_UP:    publishGesture("UP");    break;
      case DIR_DOWN:  publishGesture("DOWN");  break;
      case DIR_LEFT:  publishGesture("LEFT");  break;
      case DIR_RIGHT: publishGesture("RIGHT"); break;
      case DIR_NEAR:  publishGesture("NEAR");  break;
      case DIR_FAR:   publishGesture("FAR");   break;
      default:        publishGesture("UNKNOWN"); break;
    }
  }
  delay(50);
}
