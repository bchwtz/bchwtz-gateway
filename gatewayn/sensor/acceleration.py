from gatewayn.sensor.sensor import Sensor

class AccelerationSensor(Sensor):
    
    def __init__(self) -> None:
        super(AccelerationSensor, self).__init__()
        self.last_measurement: AccelerationSensor.AccelerationMeasurement = None
        self.movement_counter: int = 0
        self.accelerations: list[AccelerationSensor.AccelerationMeasurement] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        self.last_measurement = AccelerationSensor.AccelerationMeasurement(data.get("acceleration_x"), data.get("acceleration_y"), data.get("acceleration_z"), data.get("acceleration"), data.get("movement_counter"))
        self.movement_counter = data.get("movement_counter")
        self.accelerations.append(self.last_measurement)
        return

    class AccelerationMeasurement:
        def __init__(self, acc_x: float = 0.0, acc_y: float = 0.0, acc_z: float = 0.0, acc: float = 0.0, movement_counter: int = 0) -> None:
            self.acc_x: float = acc_x
            self.acc_y: float = acc_y
            self.acc_z: float = acc_z
            self.acc: float = acc
