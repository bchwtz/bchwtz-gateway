import time
from gateway.sensor.sensor import Sensor
from gateway.sensor.measurement import Measurement


class AccelerationSensor(Sensor):
    """An object of this class creates a digital representation of a acceleration sensor. This sensors measurements are of type gateway.sensor.barometer.BarometerSensor.AccelerationMeasurement.
    """
    def __init__(self) -> None:
        """ Sets up a new AccelerationSensor object
        """
        super(AccelerationSensor, self).__init__()
        self.name: str = "AccelerationSensor"
        self.measurements: list[AccelerationSensor.AccelerationMeasurement] = []
        self.crc: bytearray = bytearray()

    def read_data_from_advertisement(self, data: dict[str, any]):
        """ Reads data of an advertisement event onto the sensor's measurements and adds them to the list of Measurments.
        Arguments:
            data: The advertisements data as a dict.
        """
        if data is None:
            self.logger.warn("data was none!")
            return
        self.last_measurement = AccelerationSensor.AccelerationMeasurement(data.get("acceleration_x"), data.get("acceleration_y"), data.get("acceleration_z"), data.get("acceleration"), data.get("movement_counter"))
        self.movement_counter = data.get("movement_counter")
        self.measurements.append(self.last_measurement)
        return

    class AccelerationMeasurement(Measurement):
        """ AccelerationMeasurements store data in a vector + acceleration force.
        """
        def __init__(self, acc_x: float = 0.0, acc_y: float = 0.0, acc_z: float = 0.0, acc: float = 0.0, movement_counter: int = 0, sequence_number: int = 0, data_format: int = 0, recorded_time: float = 0.0, gathering_type: str = "advertisement") -> None:
            """ Creates a new AccelerationMeasurements object.
            
            Arguments:
                acc_x: x-vectorpart of the force
                acc_y: y-vectorpart of the force
                acc_z: z-vectorpart of the force
                acc: acc-force scalar
                sequence_number: Stores the index of the current measurement
                data_format: Data format the measurement was received in (is inside the message from the tag)
                movement_counter: increments on each detected movement
            """
            if recorded_time == 0.0:
                recorded_time = time.time()
            self.acc_x: float = acc_x
            self.acc_y: float = acc_y
            self.acc_z: float = acc_z
            self.acc: float = acc
            self.gathering_type = gathering_type
            self.sequence_number: int = sequence_number
            self.data_format: int = data_format
            self.movement_counter: int = movement_counter
            self.recorded_time: float = recorded_time

        def get_props(self) -> dict:
            """ Returns self object as a dict for serialization.
                Returns:
                    dict of properties
            """
            props: dict = self.__dict__
            props["measurements"] = ""
            return props