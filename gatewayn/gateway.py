import logging
from time import sleep, time
from gatewayn.hub.hub import Hub

class Gateway:

    def __init__(self) -> None:
        self.hub = Hub()
        self.logger = logging.getLogger("Gateway")
        self.logger.setLevel(logging.INFO)
        self.hub.discover_tags()
        for tag in self.hub.tags:
            tag.get_config()
        

    def run(self) -> None:
        while True:
            self.hub.discover_tags()
            sleep(20)