from gatewayn.sensor.sensor import Sensor

class HumiditySensor(Sensor):
    
    def __init__(self) -> None:
        super(HumiditySensor, self).__init__()
        self.last_humidity: float = 0.0
        self.humidities: list[float] = []