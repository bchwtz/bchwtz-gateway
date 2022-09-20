package commandinterface

import "github.com/google/uuid"

type CommandRequest struct {
	Name    string      `json:"name"`
	ID      uuid.UUID   `json:"id"`
	Payload interface{} `json:"payload"`
}

func NewCommandRequest(name string, payload interface{}) CommandRequest {
	uid := uuid.New()
	cr := CommandRequest{
		ID:      uid,
		Name:    name,
		Payload: payload,
	}
	return cr
}
