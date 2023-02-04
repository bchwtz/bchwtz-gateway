package commandinterface

import (
	"github.com/google/uuid"
)

// CommandRequest - Message for MQTT broker
type CommandRequest struct {
	Topic   string      `json:"-"`
	ID      uuid.UUID   `json:"id"`
	Payload interface{} `json:"payload"`
}

// NewCommandRequest - issues a new CommandRequest
func NewCommandRequest(topic string, payload interface{}) CommandRequest {
	uid := uuid.New()
	cr := CommandRequest{
		ID:      uid,
		Topic:   topic,
		Payload: payload,
	}
	return cr
}
