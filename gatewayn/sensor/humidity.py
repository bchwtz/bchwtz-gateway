from gatewayn.sensor.sensor import Sensor

class HumiditySensor(Sensor):
    
    def __init__(self) -> None:
        super(HumiditySensor, self).__init__()
        self.name: str = "HumiditySensor"
        self.last_measurement: float = 0.0
        self.measurements: list[float] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        self.last_measurement = data.get("humidity")
        self.measurements.append(self.last_measurement)
        self.logger.debug(f"read humidity: {self.last_measurement}")
        return