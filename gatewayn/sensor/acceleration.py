import time
from gatewayn.sensor.sensor import Sensor
from gatewayn.sensor.measurement import Measurement


class AccelerationSensor(Sensor):
    
    def __init__(self) -> None:
        super(AccelerationSensor, self).__init__()
        self.name: str = "AccelerationSensor"
        self.measurements: list[AccelerationSensor.AccelerationMeasurement] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        self.last_measurement = AccelerationSensor.AccelerationMeasurement(data.get("acceleration_x"), data.get("acceleration_y"), data.get("acceleration_z"), data.get("acceleration"), data.get("movement_counter"))
        self.movement_counter = data.get("movement_counter")
        self.measurements.append(self.last_measurement)
        return

    class AccelerationMeasurement(Measurement):
        def __init__(self, acc_x: float = 0.0, acc_y: float = 0.0, acc_z: float = 0.0, acc: float = 0.0, movement_counter: int = 0, sequence_number: int = 0, data_format: int = 0) -> None:
            self.acc_x: float = acc_x
            self.acc_y: float = acc_y
            self.acc_z: float = acc_z
            self.acc: float = acc
            self.sequence_number: int = sequence_number
            self.data_format: int = data_format
            self.movement_counter: int = movement_counter
            self.recorded_time: float = time.time()

        def get_props(self):
            return self.__dict__
