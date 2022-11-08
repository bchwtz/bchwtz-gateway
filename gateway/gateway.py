import logging
from threading import Thread
from time import sleep, time
from gateway.hub.hub import Hub
import paho.mqtt.client as mqtt
from gateway.config import Config
import asyncio


class Gateway:
    """ This class is a demo server for the gateway. It will write all its outputs to a specified MQTT-broker and will read commands from the same broker.
    """
    def __init__(self) -> None:
        """ Sets up a new gateway. Just a simple constructor.
        """
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

        self.hub.mqtt_client.connect(host=Config.GlobalConfig.mqtt_broker.value)
        self.hub.mqtt_client.loop_start()


    async def get_advertisements(self) -> None:
        """ Runs the get_advertisements command as a loop. Should consider to rename this method to run.
        """
        while True:
            print("running")
            await self.hub.listen_for_advertisements()
            # sleep(20)

    async def run_discovery(self) -> None:
        """ Runs the get_advertisements command as a loop. Should consider to rename this method to run.
        """
        while True:
            print("running")
            await self.hub.discover_tags()