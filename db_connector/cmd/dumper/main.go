package main

import (
	"github.com/bchwtz-fhswf/gateway/db_connector/internal/gateway"
	"github.com/sirupsen/logrus"
	"github.com/systematiccaos/going-forward/util"
)

func main() {
	util.SetupLogs()
	logrus.SetLevel(logrus.TraceLevel)
	gw := gateway.NewDumper()
	logrus.Println(gw)
}
