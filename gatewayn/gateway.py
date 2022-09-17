import logging
from time import sleep, time
from gatewayn.hub.hub import Hub
import paho.mqtt.client as mqtt
from gatewayn.config import Config
class Gateway:

    def __init__(self) -> None:
        self.hub = Hub()
        self.hub.set_gateway(self)
        self.logger = logging.getLogger("Gateway")
        self.logger.setLevel(logging.INFO)
        self.hub.discover_tags()
        self.mqtt_client = mqtt.Client(client_id="gateway_client", clean_session = True, userdata = None, transport = "tcp")
        self.mqtt_client.username_pw_set(username=Config.GlobalConfig.mqtt_user, password=Config.GlobalConfig.mqtt_password)
        self.mqtt_client.connect(Config.GlobalConfig.mqtt_address)
        for tag in self.hub.tags:
            tag.get_config()
        self.mqtt_client.loop_start()

    def run(self) -> None:
        while True:
            self.hub.discover_tags()
            sleep(20)