/*
  ESP32 Gesture Sensor
  Reads gesture data and communicates with main computer
*/

#include <Wire.h>
// TODO: Add appropriate gesture sensor library

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 Gesture Sensor Initialized");
  // TODO: Initialize gesture sensor
  // TODO: Setup WiFi/BLE communication
}

void loop() {
  // TODO: Read gesture data
  // TODO: Send data to main application
  delay(100);
}
