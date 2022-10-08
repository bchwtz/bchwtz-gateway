import time
from gatewayn.sensor.sensor import Sensor
from gatewayn.sensor.measurement import Measurement


class BarometerSensor(Sensor):

    def __init__(self) -> None:
        super(BarometerSensor, self).__init__()
        self.name: str = "BarometerSensor"
        self.measurements: list[BarometerSensor.PressureMeasurement] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        measurement = BarometerSensor.PressureMeasurement(pressure=data.get("pressure", 0), sequence_number=data.get("sequence_number", 0), data_format=data.get("sequence_number", 0))
        self.measurements.append(measurement)
        self.logger.debug(f"read pressure: {measurement}")
        return

    class PressureMeasurement(Measurement):
        def __init__(self, pressure: float = 0.0, sequence_number: int = 0, data_format: int = 0) -> None:
            self.pressure: float = pressure
            self.sequence_number: int = sequence_number
            self.data_format: int = data_format
            self.recorded_time: float = time.time()

        def get_props(self):
            return self.__dict__
