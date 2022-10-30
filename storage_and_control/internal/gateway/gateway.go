// This package provides a cli and db-dumper service for https://bchwtz.github.io/bchwtz-gateway/
package gateway

import (
	"github.com/bchwtz/bchwtz-gateway/storage_and_control/internal/model"
	"github.com/systematiccaos/going-forward/mqtt"
)

// gateway - responsible to store global environment for the services
type gateway struct {
	mqclient                  mqtt.Client
	hub                       model.Hub
	get_advertisement_channel chan mqtt.MQTTSubscriptionMessage
}
