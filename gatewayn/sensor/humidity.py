import time
from gatewayn.sensor.sensor import Sensor
from gatewayn.sensor.measurement import Measurement

class HumiditySensor(Sensor):
    
    def __init__(self) -> None:
        super(HumiditySensor, self).__init__()
        self.name: str = "HumiditySensor"
        self.measurements: list[HumiditySensor.HumidityMeasurement] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        self.measurement = HumiditySensor.HumidityMeasurement(humidity=data.get("humidity", 0.0), sequence_number=data.get("sequence_number"), data_format=data.get("data_format"))
        self.measurements.append(self.measurement)
        self.logger.debug(f"read humidity: {self.measurement}")
        return

    class HumidityMeasurement(Measurement):
        def __init__(self, humidity: float=0.0, sequence_number: int = 0, data_format: int = 0) -> None:
            self.humidity: float = humidity
            self.sequence_number: int = sequence_number
            self.data_format: int = data_format
            self.recorded_time: float = time.time()

        def get_props(self):
            return self.__dict__
