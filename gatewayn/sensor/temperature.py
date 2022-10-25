import time
from gatewayn.sensor.measurement import Measurement
from gatewayn.sensor.sensor import Sensor

class TemperatureSensor(Sensor):
    """An object of this class creates a digital representation of a temperature sensor. This sensor's measurements are of type gatewayn.sensor.temperature.TemperatureSensor.TemperatureMeasurement.

    """
    def __init__(self) -> None:
        """ Sets up a new TemperatureSensor object
        """
        super(TemperatureSensor, self).__init__()
        self.name: str = "TemperatureSensor"
        self.measurements: list[TemperatureSensor.TemperatureMeasurement] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        """ Reads data of an advertisement event onto the sensor's measurements and adds them to the list of Measurments.
        """
        self.measurement = TemperatureSensor.TemperatureMeasurement(temperature=data.get("temperature", 0.0), sequence_number=data.get("sequence_number", 0), data_format=data.get("data_format", 0))
        self.measurements.append(self.measurement)
        self.logger.debug(f"read temperature: {self.measurement}")
        return

    class TemperatureMeasurement(Measurement):
        """TemperatureMeasurements store data in degrees celsius.

        """
        def __init__(self, temperature: float = 0.0, sequence_number: int = 0, data_format: int = 0) -> None:
            """ Creates a new TemperatureMeasurements object.
            
            Arguments:
                temperature: Temperature in degrees celcius
                sequence_number: Stores the index of the current measurement
                data_format: Data format the measurement was received in (is inside the message from the tag)
            """
            self.temperature: float = temperature
            self.sequence_number: int = sequence_number
            self.data_format: int = data_format
            self.recorded_time: float = time.time()


        def get_props(self) -> dict:
            """ Returns self object as a dict for serialization.
                Returns:
                    dict of properties
            """
            return self.__dict__
