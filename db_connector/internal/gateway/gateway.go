package gateway

import (
	"github.com/bchwtz-fhswf/gateway/db_connector/internal/model"
	"github.com/systematiccaos/going-forward/mqtt"
)

type gateway struct {
	mqclient                  mqtt.Client
	hub                       model.Hub
	get_advertisement_channel chan mqtt.MQTTSubscriptionMessage
}
