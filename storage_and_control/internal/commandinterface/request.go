package commandinterface

import "github.com/google/uuid"

// CommandRequest - Message for MQTT broker
type CommandRequest struct {
	Name    string      `json:"name"`
	ID      uuid.UUID   `json:"id"`
	Payload interface{} `json:"payload"`
}

// NewCommandRequest - issues a new CommandRequest
func NewCommandRequest(name string, payload interface{}) CommandRequest {
	uid := uuid.New()
	cr := CommandRequest{
		ID:      uid,
		Name:    name,
		Payload: payload,
	}
	return cr
}
