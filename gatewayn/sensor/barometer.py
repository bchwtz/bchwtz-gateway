from gatewayn.sensor.sensor import Sensor

class BarometerSensor(Sensor):

    def __init__(self) -> None:
        super(BarometerSensor, self).__init__()
        self.last_pressure: float = 0.0
        self.pressures: list[float] = []