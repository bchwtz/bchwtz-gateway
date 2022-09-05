/*
Copyright © 2022 NAME HERE <EMAIL ADDRESS>
*/
package main

import (
	"github.com/bchwtz-fhswf/gateway/client/cmd"
	"github.com/bchwtz-fhswf/gateway/client/tools"
)

func main() {
	tools.SetupLogs()
	cmd.Execute()
}
