import logging
from threading import Thread
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
        self.hub.mqtt_client = self.mqtt_client
        self.hub.mqtt_client.on_message = self.hub.mqtt_on_command
        self.hub.mqtt_client.on_connect = self.hub.mqtt_on_connect
        self.logger.info("connecting to mqtt")
        asyncio.get_event_loop().create_task(self.hub.subscribe_to_log_events())

        self.hub.mqtt_client.connect(host=Config.GlobalConfig.mqtt_address.value)
        self.hub.mqtt_client.loop_start()


    async def get_advertisements(self) -> None:
        while True:
            print("running")
            await self.hub.listen_for_advertisements()
            # sleep(20)