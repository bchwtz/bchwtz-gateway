package gateway

import (
	"encoding/json"
	"errors"
	"os"
	"reflect"

	"github.com/bchwtz/bchwtz-gateway/storage_and_control/internal/commandinterface"
	"github.com/joho/godotenv"
	"github.com/sirupsen/logrus"
	"github.com/systematiccaos/going-forward/mqtt"
	"github.com/urfave/cli"
)

// globals for the cli program
type CLI struct {
	gateway
	// cli-app - used to run the whole program
	App *cli.App
	// current MQTT-topic
	topic string
	// current MQTT-command result Topic
	restopic string
}

// enum containing the environment-variables for the MQTT-config
type topicenv string

const (
	// the environment-variable of the MQTT-topic that should be used to send commands
	COMMAND_TOPIC topicenv = "TOPIC_COMMAND"
	// the environment-variable of the MQTT-topic that should be used to receive command responses
	COMMAND_RES_TOPIC topicenv = "TOPIC_COMMAND_RES"
)

// returns a new CLI app that it creates - if any errors occur the program will quit faulty
func NewCLI() CLI {
	if err := godotenv.Load("../.env"); err != nil {
		logrus.Errorln(err)
	}
	cliapp := CLI{}
	if err := cliapp.mqclient.Connect(os.Getenv("MQTT_BROKER")+":"+os.Getenv("MQTT_PORT"), os.Getenv("MQTT_CLIENTID"+"_cmd_ctrl"), os.Getenv("MQTT_USER"), os.Getenv("MQTT_PASSWORD"), true); err != nil {
		logrus.Fatalln(err)
	}
	cliapp.configure()
	return cliapp
}

// waits for a response and handles it (prints it)
func (c *CLI) handleComms(req commandinterface.CommandRequest) error {
	logrus.Infoln("waiting for a response from the gateway...")
	logrus.Println("topic: " + c.topic)
	reqbt, err := json.Marshal(&req)
	if err != nil {
		logrus.Errorln(err)
		return err
	}
	// opens an internal answerchannel
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
		// let's compare the received RequestID with the one we are waiting for... - if it is not ours listen for the next message
		if res.RequestID.String() != req.ID.String() {
			continue
		}
		// it has to be our message now - let us acknowledge the reception
		answer.Message.Ack()
		logrus.Infoln(res.Payload)
		// let us check if the message was an error
		return c.resHasErr(res)
	}
}

// traverse through the message and check if it contains a soft error
func (c *CLI) resHasErr(res commandinterface.CommandResponse) error {
	if reflect.TypeOf(res.Payload).Kind() == reflect.Map {
		resmap := res.Payload.(map[string]interface{})
		if resmap["status"] == "error" {
			err := errors.New(resmap["msg"].(string))
			logrus.Errorln(err)
			return err
		}
	}
	return nil
}

// configure the cli-app
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
						Action: func(cCtx *cli.Context) error {
							args := ""
							if cCtx.Args().Present() {
								args = cCtx.Args().First()
							}
							req := commandinterface.NewCommandRequest("get_tags", args)
							return c.handleComms(req)
						},
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
