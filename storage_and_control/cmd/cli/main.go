package main

import (
	"os"

	"github.com/bchwtz-fhswf/gateway/storage_and_control/internal/gateway"
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
