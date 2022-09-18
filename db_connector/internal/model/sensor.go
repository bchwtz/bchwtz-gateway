package model

type Sensor interface {
	GetName() string
	GetMeasurements() []interface{}
}

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

type AccelerationSensor struct {
	BasicSensor
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
