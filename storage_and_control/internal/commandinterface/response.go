package commandinterface

import "github.com/google/uuid"

// CommandResponse - Response to a sent MQTT-command containing its ID
type CommandResponse struct {
	Name      string      `json:"name"`
	ID        uuid.UUID   `json:"id"`
	RequestID uuid.UUID   `json:"request_id"`
	Payload   interface{} `json:"payload"`
}
