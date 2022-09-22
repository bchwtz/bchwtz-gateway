package gateway

import (
	"encoding/json"
	"os"

	"github.com/bchwtz-fhswf/gateway/db_connector/internal/commandinterface"
	"github.com/joho/godotenv"
	"github.com/sirupsen/logrus"
	"github.com/systematiccaos/going-forward/mqtt"
	"github.com/urfave/cli"
)

type CLI struct {
	gateway
	App      *cli.App
	topic    string
	restopic string
}

type topicenv string

const (
	COMMAND_TOPIC     topicenv = "TOPIC_COMMAND"
	COMMAND_RES_TOPIC topicenv = "TOPIC_COMMAND_RES"
)

func NewCLI() CLI {
	if err := godotenv.Load("../.env"); err != nil {
		logrus.Errorln(err)
	}
	cliapp := CLI{}
	if err := cliapp.mqclient.Connect(os.Getenv("MQTT_BROKER")+":"+os.Getenv("MQTT_PORT"), os.Getenv("MQTT_CLIENTID"), os.Getenv("MQTT_USER"), os.Getenv("MQTT_PASSWORD"), true); err != nil {
		logrus.Fatalln(err)
	}
	cliapp.configure()
	return cliapp
}

func (c *CLI) handleComms(req commandinterface.CommandRequest) error {
	logrus.Infoln("waiting for a response from the gateway...")
	logrus.Println("topic: " + c.topic)
	reqbt, err := json.Marshal(&req)
	if err != nil {
		logrus.Errorln(err)
		return err
	}
	answerch := make(chan mqtt.MQTTSubscriptionMessage)
	logrus.Info("subscribing to " + c.restopic)
	c.mqclient.Subscribe(c.restopic, answerch)
	tk := c.mqclient.Publish(c.topic, reqbt)
	if tk.Wait() && tk.Error() != nil {
		logrus.Errorln(tk.Error())
		return tk.Error()
	}
	for {
		answer := <-answerch
		res := commandinterface.CommandResponse{}
		if err := json.Unmarshal(answer.Message.Payload(), &res); err != nil {
			return err
		}
		if res.RequestID.String() != req.ID.String() {
			continue
		}
		answer.Message.Ack()
		logrus.Println(res.Payload)
		return nil
	}
}

func (c *CLI) configure() {
	c.topic = os.Getenv(string(COMMAND_TOPIC))
	c.restopic = os.Getenv(string(COMMAND_RES_TOPIC))
	c.App = &cli.App{
		Name:  "gateway command line interface",
		Usage: "This is a cli for the ble_gateway project. Please use --help to get to know more about the commands!",

		Commands: []cli.Command{
			{
				Name:  "gateway",
				Usage: "attributes of the gateway itself",
			},
			{
				Name: "tags",
				Aliases: []string{
					"tag",
				},
				Subcommands: []cli.Command{
					{
						Name: "set",
						Subcommands: []cli.Command{
							{
								Name: "time",
								Action: func(cCtx *cli.Context) error {
									var args []string
									if cCtx.Args().Present() {
										args = append(args, cCtx.Args().First())
										args = append(args, cCtx.Args().Get(1))
									}
									req := commandinterface.NewCommandRequest("set_time", args)
									return c.handleComms(req)
								},
							},
						},
					},
					{
						Name:      "get",
						ArgsUsage: "first arg is the tags name - if none is set every tag will be asked for its time and config",
						Subcommands: []cli.Command{
							{
								Name: "time",
								Action: func(cCtx *cli.Context) error {
									args := ""
									if cCtx.Args().Present() {
										args = cCtx.Args().First()
									}
									req := commandinterface.NewCommandRequest("get_time", args)
									return c.handleComms(req)
								},
							},
							{
								Name: "config",
								Action: func(cCtx *cli.Context) error {
									logrus.Infoln("getting config")
									args := ""
									if cCtx.Args().Present() {
										args = cCtx.Args().First()
									}
									req := commandinterface.NewCommandRequest("get_config", args)
									return c.handleComms(req)
								},
							},
						},
					},
				},
				Usage: "attributes of the tags",
			},
		},
	}
}
