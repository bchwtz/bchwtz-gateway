package main

import (
	"github.com/bchwtz-fhswf/gateway/db_connector/internal/gateway"
	"github.com/sirupsen/logrus"
	"github.com/systematiccaos/going-forward/util"
)

func main() {
	util.SetupLogs()
	gw := gateway.NewDumper()
	logrus.Println(gw)
}
