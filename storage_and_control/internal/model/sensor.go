package model

// Sensor is an interface all referenced sensors have to comply to.
type Sensor interface {
	GetName() string
	GetMeasurements() []interface{}
}

// BaseStructure for all sensors
type BasicSensor struct {
	Name         string        `json:"name"`
	Measurements []interface{} `json:"measurements"`
}

func (s *BasicSensor) GetName() string        { return s.Name }
func (s *AccelerationSensor) GetName() string { return s.Name }
func (s *BarometerSensor) GetName() string    { return s.Name }
func (s *TemperatureSensor) GetName() string  { return s.Name }
func (s *HumiditySensor) GetName() string     { return s.Name }
func (s *BatterySensor) GetName() string      { return s.Name }

func (s *BasicSensor) GetMeasurements() []interface{}        { return s.Measurements }
func (s *AccelerationSensor) GetMeasurements() []interface{} { return s.Measurements }
func (s *BarometerSensor) GetMeasurements() []interface{}    { return s.Measurements }
func (s *TemperatureSensor) GetMeasurements() []interface{}  { return s.Measurements }
func (s *HumiditySensor) GetMeasurements() []interface{}     { return s.Measurements }
func (s *BatterySensor) GetMeasurements() []interface{}      { return s.Measurements }

// contains measurements for acceleration events
type AccelerationSensor struct {
	BasicSensor
}

// contains pressure measurements
type BarometerSensor struct {
	BasicSensor
}

// contains temperature measurements
type TemperatureSensor struct {
	BasicSensor
}

// contains humidity measurements
type HumiditySensor struct {
	BasicSensor
}

// contains battery measurements
type BatterySensor struct {
	BasicSensor
}
