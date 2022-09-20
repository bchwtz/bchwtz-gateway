import logging
from time import sleep, time
from gatewayn.hub.hub import Hub
import paho.mqtt.client as mqtt
from gatewayn.config import Config
import asyncio
class Gateway:

    def __init__(self) -> None:
        self.hub = Hub()
        self.logger = logging.getLogger("Gateway")
        self.logger.setLevel(logging.INFO)
        Config.load_from_environ()
        self.mqtt_client = mqtt.Client(client_id=Config.GlobalConfig.mqtt_client_id.value, clean_session = True, userdata = None, transport = "tcp")
        self.mqtt_client.username_pw_set(username=Config.GlobalConfig.mqtt_user.value, password=Config.GlobalConfig.mqtt_password.value)
        self.mqtt_client.connect(host=Config.GlobalConfig.mqtt_address.value)
        self.hub.mqtt_client = self.mqtt_client
        self.logger.info("connected successfully to mqtt")
        self.mqtt_client.loop_start()
        asyncio.get_event_loop().create_task(self.hub.subscribe_to_log_events())

    async def get_advertisements(self) -> None:
        while True:
            print("running")
            await self.hub.listen_for_advertisements()
            sleep(20)