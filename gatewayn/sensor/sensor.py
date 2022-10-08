from logging import Logger
import logging
from gatewayn.sensor.measurement import Measurement


class Sensor(object):

    def __init__(self) -> None:
        self.name = "BasicSensor"
        self.measurements: list[Measurement] = []
        self.logger = logging.getLogger("Sensor")
        self.logger.setLevel(logging.INFO)

    def read_data_from_advertisement(self, data: dict[str, any]):
        self.logger.error("read_data_from_advertisement not implemented on this type of sensor")
        return

    def get_measurement_props(self) -> list[dict]:
        measurements = []
        for m in self.measurements:
            if type(m) is not dict:
                m = m.get_props()
            measurements.append(m)
        return measurements
    
    def get_props(self):
        dct = {"name": self.name, "measurements": self.get_measurement_props()}
        # dct["measurements"] = self.get_measurement_props()
        return dct