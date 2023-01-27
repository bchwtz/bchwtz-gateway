package commandinterface

import "github.com/google/uuid"

// CommandResponse - Response to a sent MQTT-command containing its ID
type CommandResponse struct {
	Name               string      `json:"name"`
	ID                 uuid.UUID   `json:"id"`
	RequestID          uuid.UUID   `json:"request_id"`
	OngoingRequest     bool        `json:"ongoing_request"`
	RedirectTopic      string      `json:"redirect_topic"`
	AttachmentChannels []string    `json:"attachment_channels"`
	HasAttachments     bool        `json:"has_attachments"`
	Payload            interface{} `json:"payload"`
	ObjectType         string      `json:"object_type"`
}

type AttachementResponse struct {
	CommandResponse
}
