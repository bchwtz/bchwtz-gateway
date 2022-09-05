from gatewayn.sensor.sensor import Sensor

class BatterySensor(Sensor):
    
    def __init__(self):
        super(BatterySensor, self).__init__()
        self.name: str = "BatterySensor"
        self.last_measurement: float = 0
        self.measurements: list[float] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        self.last_measurement = data.get("battery") / 1000
        self.measurements.append(self.last_measurement)
        self.logger.debug(f"read voltage: {self.last_measurement}")
        return