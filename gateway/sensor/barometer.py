import time
from gateway.sensor.sensor import Sensor
from gateway.sensor.measurement import Measurement


class BarometerSensor(Sensor):
    """An object of this class creates a digital representation of a barometer sensor. This sensors measurements are of type gateway.sensor.barometer.BarometerSensor.PressureMeasurement.
    """
    def __init__(self) -> None:
        """ Sets up a new BarometerSensor object
        """
        super(BarometerSensor, self).__init__()
        self.name: str = "BarometerSensor"
        self.measurements: list[BarometerSensor.PressureMeasurement] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        """ Reads data of an advertisement event onto the sensor's measurements and adds them to the list of Measurments.
        Arguments:
            data: The advertisements data as a dict.
        """
        measurement = BarometerSensor.PressureMeasurement(pressure=data.get("pressure", 0), sequence_number=data.get("sequence_number", 0), data_format=data.get("sequence_number", 0))
        self.measurements.append(measurement)
        self.logger.debug(f"read pressure: {measurement}")
        return

    class PressureMeasurement(Measurement):
        """ PressureMeasurements store data in kilopascal.
        """
        def __init__(self, pressure: float = 0.0, sequence_number: int = 0, data_format: int = 0) -> None:
            """ Creates a new PressureMeasurements object.
            
            Arguments:
                pressure: Pressure in kilopascal
                sequence_number: Stores the index of the current measurement
                data_format: Data format the measurement was received in (is inside the message from the tag)
            """
            self.pressure: float = pressure
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