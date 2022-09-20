package gateway

import (
	"fmt"

	"github.com/urfave/cli"
)

type CLI struct {
	gateway
	App *cli.App
}

func NewCLI() CLI {
	cliapp := CLI{}
	cliapp.configure()
	return cliapp
}

func (c *CLI) configure() {
	c.App = &cli.App{
		Name:  "gateway command line interface",
		Usage: "This is a cli for the ble_gateway project. Please use --help to get to know more about the commands!",
		Action: func(*cli.Context) error {
			fmt.Println("boom! I say!")
			return nil
		},

		Commands: []cli.Command{
			cli.Command{
				Name: "gateway",
			},
		},
	}
}
