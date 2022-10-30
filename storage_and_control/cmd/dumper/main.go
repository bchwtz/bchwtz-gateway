// This dumper expects data on the log and advertisement topics on MQTT and saves them to a given mongodb.
package main

import (
	"github.com/bchwtz/bchwtz-gateway/storage_and_control/internal/gateway"
	"github.com/sirupsen/logrus"
	"github.com/systematiccaos/going-forward/util"
)

func main() {
	util.SetupLogs()
	logrus.SetLevel(logrus.TraceLevel)
	gw := gateway.NewDumper()
	logrus.Println(gw)
}
