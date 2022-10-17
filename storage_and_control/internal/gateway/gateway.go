package gateway

import (
	"github.com/bchwtz-fhswf/gateway/storage_and_control/internal/model"
	"github.com/systematiccaos/going-forward/mqtt"
)

type gateway struct {
	mqclient                  mqtt.Client
	hub                       model.Hub
	get_advertisement_channel chan mqtt.MQTTSubscriptionMessage
}
