from gatewayn.sensor.sensor import Sensor

class BarometerSensor(Sensor):

    def __init__(self) -> None:
        super(BarometerSensor, self).__init__()
        self.name: str = "BarometerSensor"
        self.last_measurement: float = 0.0
        self.measurements: list[float] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        self.last_measurement = data.get("pressure")
        self.measurements.append(self.last_measurement)
        self.logger.debug(f"read pressure: {self.last_measurement}")
        return