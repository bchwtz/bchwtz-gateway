import time
from gateway.sensor.sensor import Sensor
from gateway.sensor.measurement import Measurement

class HumiditySensor(Sensor):
    """ An object of this class creates a digital representation of a humidity sensor. This sensor's measurements are of type gateway.sensor.humidity.HumiditySensor.HumidityMeasurement.
    """
    def __init__(self) -> None:
        """ Sets up a new HumiditySensor object
        """
        super(HumiditySensor, self).__init__()
        self.name: str = "HumiditySensor"
        self.measurements: list[HumiditySensor.HumidityMeasurement] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        """ Reads data of an advertisement event onto the sensor's measurements and adds them to the list of Measurments.
        Arguments:
            data: The advertisements data as a dict.
        """
        self.measurement = HumiditySensor.HumidityMeasurement(humidity=data.get("humidity", 0.0), sequence_number=data.get("sequence_number"), data_format=data.get("data_format"))
        self.measurements.append(self.measurement)
        self.logger.debug(f"read humidity: {self.measurement}")
        return

    class HumidityMeasurement(Measurement):
        """ HumidityMeasurements store data in percent.
        """
        def __init__(self, humidity: float=0.0, sequence_number: int = 0, data_format: int = 0) -> None:
            """ Creates a new HumidityMeasurements object.
            
            Arguments:
                humidity: Humidity in percent
                sequence_number: Stores the index of the current measurement
                data_format: Data format the measurement was received in (is inside the message from the tag)
            """
            self.humidity: float = humidity
            self.sequence_number: int = sequence_number
            self.data_format: int = data_format
            self.recorded_time: float = time.time()

        def get_props(self) -> dict:
            """ Returns self object as a dict for serialization.
                Returns:
                    dict of properties
            """
            props: dict = self.__dict__
            props["measurements"] = ""
            return props