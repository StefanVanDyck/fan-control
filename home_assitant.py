import ujson

from mqtt_as import MQTTClient


class HomeAssistantDevice:
    def __init__(self, mqtt_client: MQTTClient, name, type):
        self.mqtt_client = mqtt_client
        self.name = name
        self.type = type

    def set_mqtt_client(self, mqtt_client):
        self.mqtt_client = mqtt_client

    async def publish_discovery(self):
        topic = f"homeassistant/{self.type}/{self.name}/config"
        unique_id = f"pico_{self.type}_{self.name}"

        payload = {
            "name": self.name,
            "unique_id": unique_id,
            "qos": 0,
            "speed_range_min": 1,
            "speed_range_max": 3,
            "command_topic": f"homeassistant/{self.type}/{self.name}/on/set",
            "state_topic": f"homeassistant/{self.type}/{self.name}/on/state",
            "percentage_state_topic": f"homeassistant/{self.type}/{self.name}/speed/percentage_state",
            "percentage_command_topic": f"homeassistant/{self.type}/{self.name}/speed/percentage",
        }

        # Convert payload to JSON string for publishing
        payload_json = ujson.dumps(payload)

        # Print the payload for debugging
        print(f"Publishing to {topic}: {payload_json}")

        await self.mqtt_client.publish(topic, ujson.dumps(payload))

    async def subscribe_to_command(self):
        await self.mqtt_client.subscribe(f"homeassistant/{self.type}/{self.name}/speed/percentage")

    async def publish_state(self, value):
        state_topic = f"homeassistant/{self.type}/{self.name}/on/state"

        # Print the payload for debugging
        print(f"Publishing to {state_topic}: {value}")

        await self.mqtt_client.publish(state_topic, value)

    async def publish_percentage_state(self, value):
        state_topic = f"homeassistant/{self.type}/{self.name}/speed/percentage_state"

        # Print the payload for debugging
        print(f"Publishing to {state_topic}: {value}")

        await self.mqtt_client.publish(state_topic, value)

