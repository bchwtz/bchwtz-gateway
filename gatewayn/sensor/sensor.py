from logging import Logger
import logging


class Sensor:

    def __init__(self) -> None:
        self.name = "BasicSensor"
        self.logger = logging.getLogger("Sensor")
        self.logger.setLevel(logging.INFO)

    def read_data_from_advertisement(self, data: dict[str, any]):
        self.logger.error("read_data_from_advertisement not implemented on this type of sensor")
        return