from gatewayn.sensor.sensor import Sensor

class TemperatureSensor(Sensor):
    
    def __init__(self) -> None:
        super(TemperatureSensor, self).__init__()
        self.name: str = "TemperatureSensor"
        self.last_measurement: float = 0.0
        self.measurements: list[float] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        self.last_measurement = data.get("temperature")
        self.measurements.append(self.last_measurement)
        self.logger.debug(f"read temperature: {self.last_measurement}")
        return