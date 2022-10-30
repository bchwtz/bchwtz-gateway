// The cli-application for the ble_gateway can be run on any linux system, connects to MQTT and sends messages to the gateway to configure or contact ble-tags.
package main

import (
	"os"

	"github.com/bchwtz/bchwtz-gateway/storage_and_control/internal/gateway"
	"github.com/sirupsen/logrus"
	"github.com/systematiccaos/going-forward/util"
)

func main() {
	util.SetupLogs()
	cli := gateway.NewCLI()
	if err := cli.App.Run(os.Args); err != nil {
		logrus.Fatalln(err)
	}
}
