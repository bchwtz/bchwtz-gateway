from gatewayn.sensor.sensor import Sensor

class HumiditySensor(Sensor):
    
    def __init__(self) -> None:
        super(HumiditySensor, self).__init__()
        self.last_humidity: float = 0.0
        self.humidities: list[float] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        self.last_humidity = data.get("humidity")
        self.humidities.append(self.last_humidity)
        self.logger.debug(f"read humidity: {self.last_humidity}")
        return