from gatewayn.sensor.sensor import Sensor

class TemperatureSensor(Sensor):
    
    def __init__(self) -> None:
        super(TemperatureSensor, self).__init__()
        self.name: str = "TemperatureSensor"
        self.measurements: list[TemperatureSensor.TemperatureMeasurement] = []

    def read_data_from_advertisement(self, data: dict[str, any]):
        self.measurement = TemperatureSensor.TemperatureMeasurement(temperature=data.get("temperature", 0.0), sequence_number=data.get("sequence_number", 0), data_format=data.get("data_format", 0))
        self.measurements.append(self.measurement)
        self.logger.debug(f"read temperature: {self.measurement}")
        return

    class TemperatureMeasurement:
        def __init__(self, temperature: float = 0.0, sequence_number: int = 0, data_format: int = 0) -> None:
            self.temperature: float = temperature
            self.sequence_number: int = sequence_number
            self.data_format: int = data_format

        def get_props(self):
            return self.__dict__
