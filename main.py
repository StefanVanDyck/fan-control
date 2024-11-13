import gc

import time
import uasyncio as asyncio
from machine import Pin, reset

from home_assistant import HomeAssistantDevice
from mqtt_as import MQTTClient, config

CLIENT_ID = "Pico"
MQTT_KEEP_ALIVE = 180
MQTT_UPDATE_INTERVAL = 30

led = Pin("LED", Pin.OUT)
relay1 = Pin("GP0", Pin.OUT)
relay2 = Pin("GP1", Pin.OUT)

# Define configuration
config['server'] = '192.168.129.14'
config['port'] = 1883
config['ssid'] = 'xxx'
config['wifi_pw'] = 'xxx'
config["queue_len"] = 1  # Use event interface with default queue size
MQTTClient.DEBUG = False  # Optional: print diagnostic messages

gc.collect()


async def main():
    current_speed = b"1"
    mqtt_client = MQTTClient(config)
    home_assistant = HomeAssistantDevice(mqtt_client, "ventilation", "fan")

    async def messages(client):  # Respond to incoming messages
        nonlocal current_speed
        async for topic, msg, retained in client.queue:
            print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
            if topic == b'homeassistant/fan/ventilation/speed/percentage':
                if msg == b"1":
                    relay1.high()
                    relay2.high()
                    current_speed = b"1"
                elif msg == b"2":
                    relay1.low()
                    relay2.high()
                    current_speed = b"2"
                elif msg == b"3":
                    relay1.high()
                    relay2.low()
                    current_speed = b"3"
                else:
                    print("Received unknown preset value")

            await home_assistant.publish_percentage_state(current_speed)

    async def up(client):  # Respond to connectivity being (re)established
        while True:
            await client.up.wait()  # Wait on an Event
            client.up.clear()
            print("Connected to MQTT broker")
            await home_assistant.subscribe_to_command()
            await home_assistant.publish_discovery()

    print("Connecting")

    try:
        await mqtt_client.connect()

        asyncio.create_task(messages(mqtt_client))
        asyncio.create_task(up(mqtt_client))

        while True:
            await asyncio.sleep(MQTT_UPDATE_INTERVAL)
            await home_assistant.publish_state(b"ON")
            await home_assistant.publish_percentage_state(current_speed)

    finally:
        mqtt_client.close()


try:
    asyncio.run(main())
except Exception as e:
    import sys

    print("Fatal error while running program")
    sys.print_exception(e)
    raise
finally:
    time.sleep(10)
    reset()

