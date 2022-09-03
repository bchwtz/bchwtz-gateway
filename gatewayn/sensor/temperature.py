from gatewayn.sensor.sensor import Sensor

class TemperatureSensor(Sensor):
    
    def __init__(self) -> None:
        super(TemperatureSensor, self).__init__()
        self.last_temperature: float = 0.0
        self.temperatures: list[float] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        self.last_temperature = data.get("temperature")
        self.temperatures.append(self.last_temperature)
        self.logger.debug(f"read temperature: {self.last_temperature}")
        return