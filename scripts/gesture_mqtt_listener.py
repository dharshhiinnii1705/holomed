import sys
try:
    import paho.mqtt.client as mqtt
except Exception:
    print('paho-mqtt required. Install with: pip install paho-mqtt')
    sys.exit(1)


MQTT_BROKER = "192.168.1.10"  # change to your broker
MQTT_PORT = 1883
MQTT_TOPIC = "holomed/gesture"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected to MQTT broker')
        client.subscribe(MQTT_TOPIC)
    else:
        print('Connect failed with rc', rc)


def on_message(client, userdata, msg):
    print('Gesture:', msg.payload.decode())


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()


if __name__ == '__main__':
    main()
