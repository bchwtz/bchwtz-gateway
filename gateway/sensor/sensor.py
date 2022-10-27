from logging import Logger
import logging
from gateway.sensor.measurement import Measurement


class Sensor(object):
    """An object of this class creates a digital representation of a sensor. Every 
    sensor has a name and measurements of a defined class.

    """
    def __init__(self) -> None:
        """Sets up a new sensor
        """
        self.name = "BasicSensor"
        self.measurements: list[Measurement] = []
        self.logger = logging.getLogger("Sensor")
        self.logger.setLevel(logging.INFO)

    def read_data_from_advertisement(self, data: dict[str, any]):
        """Reads data that was discovered during an advertisement event, especially for this sensor type.

        Arguments:
            data: dict with the data of the advertisement
        """
        self.logger.error("read_data_from_advertisement not implemented on this type of sensor")
        return

    def get_measurement_props(self) -> list[dict]:
        """Returns all measurements of this sensor as a list of dicts to be json-serializable.

        Returns:
            Measurements as a list of dicts.
        """
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