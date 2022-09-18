package model

type Tag struct {
	Address  string        `json:"address"`
	BLEDev   BLEDevice     `json:"ble_device"`
	Name     string        `json:"name"`
	Sensors  []BasicSensor `json:"sensors"`
	Config   TagConfig     `json:"config"`
	Online   bool          `json:"online"`
	LastSeen float32       `json:"last_seen"`
}
