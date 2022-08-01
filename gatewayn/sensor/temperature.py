from gatewayn.sensor.sensor import Sensor

class TemperatureSensor(Sensor):
    
    def __init__(self) -> None:
        super(TemperatureSensor, self).__init__()
        self.last_temp: float = 0.0
        self.temperatures: list[float] = []