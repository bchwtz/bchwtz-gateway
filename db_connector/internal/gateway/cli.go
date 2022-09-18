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
	return CLI{}
}

func (c *CLI) configure() {
	c.App = &cli.App{
		Name:  "boom",
		Usage: "make an explosive entrance",
		Action: func(*cli.Context) error {
			fmt.Println("boom! I say!")
			return nil
		},
	}
}
