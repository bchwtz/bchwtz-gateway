package model

// complies to the python-implementation of a tag_config
type TagConfig struct {
	Samplerate   int    `json:"samplerate"`
	Resolution   int    `json:"resolution"`
	Scale        int    `json:"scale"`
	DSPFunction  int    `json:"dsp_function"`
	DSPParameter int    `json:"dsp_parameter"`
	Mode         string `json:"mode"`
	Divider      int    `json:"divider"`
}
