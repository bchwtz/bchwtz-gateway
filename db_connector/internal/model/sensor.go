package model

type Sensor interface {
	GetName() string
	GetLastMeasurement() interface{}
	GetMeasurements() []interface{}
}

type BasicSensor struct {
	Name            string        `json:"name"`
	LastMeasurement interface{}   `json:"last_measurement"`
	Measurements    []interface{} `json:"measurements"`
}

func (s *BasicSensor) GetName() string        { return s.Name }
func (s *AccelerationSensor) GetName() string { return s.Name }
func (s *BarometerSensor) GetName() string    { return s.Name }
func (s *TemperatureSensor) GetName() string  { return s.Name }
func (s *HumiditySensor) GetName() string     { return s.Name }
func (s *BatterySensor) GetName() string      { return s.Name }

func (s *BasicSensor) GetLastMeasurement() interface{}        { return s.LastMeasurement }
func (s *AccelerationSensor) GetLastMeasurement() interface{} { return s.LastMeasurement }
func (s *BarometerSensor) GetLastMeasurement() interface{}    { return s.LastMeasurement }
func (s *TemperatureSensor) GetLastMeasurement() interface{}  { return s.LastMeasurement }
func (s *HumiditySensor) GetLastMeasurement() interface{}     { return s.LastMeasurement }
func (s *BatterySensor) GetLastMeasurement() interface{}      { return s.LastMeasurement }

func (s *BasicSensor) GetMeasurements() []interface{}        { return s.Measurements }
func (s *AccelerationSensor) GetMeasurements() []interface{} { return s.Measurements }
func (s *BarometerSensor) GetMeasurements() []interface{}    { return s.Measurements }
func (s *TemperatureSensor) GetMeasurements() []interface{}  { return s.Measurements }
func (s *HumiditySensor) GetMeasurements() []interface{}     { return s.Measurements }
func (s *BatterySensor) GetMeasurements() []interface{}      { return s.Measurements }

func (s *AccelerationSensor) GetMovementCounter() int { return s.MovementCounter }

type AccelerationSensor struct {
	BasicSensor
	MovementCounter int `json:"movement_counter"`
}

type BarometerSensor struct {
	BasicSensor
}

type TemperatureSensor struct {
	BasicSensor
}

type HumiditySensor struct {
	BasicSensor
}

type BatterySensor struct {
	BasicSensor
}
