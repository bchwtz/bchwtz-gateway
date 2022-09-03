from gatewayn.sensor.sensor import Sensor

class BarometerSensor(Sensor):

    def __init__(self) -> None:
        super(BarometerSensor, self).__init__()
        self.last_pressure: float = 0.0
        self.pressures: list[float] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        self.last_pressure = data.get("pressure")
        self.pressures.append(self.last_pressure)
        self.logger.debug(f"read pressure: {self.last_pressure}")
        return