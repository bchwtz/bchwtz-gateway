from gatewayn.sensor.sensor import Sensor

class BatterySensor(Sensor):
    
    def __init__(self):
        super(BatterySensor, self).__init__()
        self.last_voltage: float = 0
        self.voltages: list[float] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        self.last_voltage = data.get("battery") / 1000
        self.voltages.append(self.last_voltage)
        self.logger.debug(f"read voltage: {self.last_voltage}")
        return