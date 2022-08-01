from gatewayn.sensor.sensor import Sensor

class AccelerationSensor(Sensor):
    
    def __init__(self) -> None:
        super(AccelerationSensor, self).__init__()
        self.last_acc_x: float = 0.0
        self.last_acc_y: float = 0.0
        self.last_acc_z: float = 0.0
        self.accelerations: list[list[float]] = []