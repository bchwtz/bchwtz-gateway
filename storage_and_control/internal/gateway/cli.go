package gateway

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"reflect"
	"time"

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
	// current MQTT-command result Topic
	tag_topic_pre string
	// current MQTT-command result Topic
	tags_topic_pre string
	// outputFile
	output_file string
	// running workerloops
	workerloops int
	// answerchannels
	answerch chan mqtt.MQTTSubscriptionMessage
	endedch  chan []interface{}
}

// enum containing the environment-variables for the MQTT-config
type topicenv string

const (
	// the environment-variable of the MQTT-topic that should be used to send commands
	COMMAND_TOPIC topicenv = "TOPIC_COMMAND"
	// the environment-variable of the MQTT-topic that should be used to receive command responses
	COMMAND_RES_TOPIC topicenv = "TOPIC_COMMAND_RES"
	// the environment-variable of the MQTT-topic-prefix that should be used to send commands to specific tags
	COMMAND_TOPIC_TAG_PREFIX topicenv = "TOPIC_TAG_PREFIX"
	// the environment-variable of the MQTT-topic-prefix that should be used to send commands to specific tags
	COMMAND_TOPIC_TAGS_PREFIX topicenv = "TOPIC_TAGS_PREFIX"
)

// returns a new CLI app that it creates - if any errors occur the program will quit faulty
func NewCLI() CLI {
	if err := godotenv.Load("../.env"); err != nil {
		logrus.Infoln(err)
	}
	cliapp := CLI{}
	if err := cliapp.mqclient.Connect(os.Getenv("MQTT_BROKER")+":"+os.Getenv("MQTT_PORT"), os.Getenv("MQTT_CLIENTID"+"_cmd_ctrl"), os.Getenv("MQTT_USER"), os.Getenv("MQTT_PASSWORD"), true); err != nil {
		logrus.Fatalln(err)
	}
	cliapp.configure()
	return cliapp
}

// waits for a response and handles it (prints it)
func (c *CLI) handleComms(req commandinterface.CommandRequest, outputfile string) error {
	logrus.Infoln("waiting for a response from the gateway...")
	logrus.Println("topic: " + req.Topic)
	c.workerloops = 1
	reqbt, err := json.Marshal(&req)
	if err != nil {
		logrus.Errorln(err)
		return err
	}
	logrus.Warnln(string(reqbt))
	// opens an internal answerchannel
	c.answerch = make(chan mqtt.MQTTSubscriptionMessage)

	logrus.Info("subscribing to " + c.restopic)
	c.mqclient.Subscribe("#", c.answerch)
	tk := c.mqclient.Publish(req.Topic, reqbt)
	if tk.Wait() && tk.Error() != nil {
		logrus.Errorln(tk.Error())
		return tk.Error()
	}
	c.endedch = make(chan []interface{})
	payloads := []interface{}{}
	go c.handleCallback(req)
	for i := 0; i < c.workerloops; i++ {
		payload := <-c.endedch
		payloads = append(payloads, payload)
		logrus.Infof("ended %s", payloads)
	}
	if outputfile != "" {
		if jout, err := json.MarshalIndent(payloads, "", "	"); jout != nil && err == nil {
			if err := os.WriteFile(outputfile, jout, 0775); err != nil {
				logrus.Errorln(err)
				return err
			}
		} else {
			logrus.Errorln(err)
			return err
		}
	}
	return nil
}

// waits for answers on channels we subscribed to earlier
func (c *CLI) handleCallback(req commandinterface.CommandRequest) error {
	payloads := []interface{}{}
	ended := false
	for {
		answer := <-c.answerch
		res := commandinterface.CommandResponse{}
		if err := json.Unmarshal(answer.Message.Payload(), &res); err != nil {
			return err
		}
		// logrus.Println(string(answer.Message.Payload()))
		if err := c.resHasErr(res); err != nil {
			logrus.Errorln(err)
			return err
		}
		// let's compare the received RequestID with the one we are waiting for... - if it is not ours listen for the next message
		if res.RequestID.String() != req.ID.String() {
			continue
		}

		// it has to be our message now - let us acknowledge the reception
		answer.Message.Ack()
		// logrus.Infoln(res.Payload)
		// if res.HasAttachments {
		// 	for _, topic := range res.AttachmentChannels {
		// 		logrus.Info("incrementing workloops to " + topic)
		// 		// c.workerloops++
		// 		// if err := c.mqclient.Subscribe(topic, c.answerch); err != nil {
		// 		// 	logrus.Warnln(err)
		// 		// 	continue
		// 		// }
		// 	}
		// 	payloads = append(payloads, res.Payload)
		// 	continue

		// }
		payloads = append(payloads, res.Payload)
		if res.OngoingRequest {
			continue
		}
		// let us check if the message was an error
		if err := c.resHasErr(res); err != nil {
			logrus.Errorln(err)
			return err
		}
		if !ended {
			c.endedch <- payloads
		}
		ended = true
		time.Sleep(10 * time.Second)
	}

	return nil
}

// traverse through the message and check if it contains a soft error
func (c *CLI) resHasErr(res commandinterface.CommandResponse) error {
	if res.Payload != nil && reflect.TypeOf(res.Payload).Kind() == reflect.Map {
		resmap := res.Payload.(map[string]interface{})
		if resmap["status"] == "error" {
			err := errors.New(resmap["msg"].(string))
			logrus.Errorln(err)
			return err
		}
	}
	return nil
}

// constructs a topic name by the given parameters and returns it
func (c *CLI) getTopicByAddressAndCommand(cCtx *cli.Context, cmd string) string {
	topic := ""
	address := ""
	if cCtx.NumFlags() > 0 {
		address = cCtx.String("address")
	}
	if address != "" {
		topic += fmt.Sprintf("%s/%s", c.tag_topic_pre, address)
	} else {
		topic += fmt.Sprintf("%ss", c.tag_topic_pre)
	}
	topic += fmt.Sprintf("/commands/%s", cmd)
	return topic
}

// configure the cli-app
func (c *CLI) configure() {
	c.topic = os.Getenv(string(COMMAND_TOPIC))
	c.restopic = os.Getenv(string(COMMAND_RES_TOPIC))
	c.tag_topic_pre = os.Getenv(string(COMMAND_TOPIC_TAG_PREFIX))
	c.tags_topic_pre = os.Getenv(string(COMMAND_TOPIC_TAGS_PREFIX))

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
					"hub",
				},
				Subcommands: []cli.Command{
					{
						Name: "set",
						Subcommands: []cli.Command{
							{
								Name: "time",
								Flags: []cli.Flag{
									&cli.StringFlag{
										Name:  "address",
										Value: "",
										Usage: "address to trigger a specific tag",
									},
								},
								Action: func(cCtx *cli.Context) error {
									var args []string
									if cCtx.Args().Present() {
										args = append(args, cCtx.Args().First())
										args = append(args, cCtx.Args().Get(1))
									}
									topic := c.getTopicByAddressAndCommand(cCtx, "set_time")
									req := commandinterface.NewCommandRequest(topic, args)
									return c.handleComms(req, "")
								},
							},
							{
								Name: "config",
								Flags: []cli.Flag{
									&cli.StringFlag{
										Name:  "address",
										Value: "",
										Usage: "address to trigger a specific tag",
									},
									&cli.StringFlag{
										Name:  "config",
										Value: "",
										Usage: "Enter the config as a json object like: {\"samplerate\": 10, \"resolution\": 10, \"scale\": 1, \"dsp_function\": 1, \"dsp_parameter\": 0, \"mode\": \"f4\", \"divider\": 1}",
									},
								},
								Action: func(cCtx *cli.Context) error {
									config := make(map[string]interface{})
									if err := json.Unmarshal([]byte(cCtx.String("config")), &config); err != nil {
										logrus.Fatalln("no valid json in config!")
									}
									topic := c.getTopicByAddressAndCommand(cCtx, "set_config")
									req := commandinterface.NewCommandRequest(topic, config)
									return c.handleComms(req, "")
								},
							},
						},
					},
					{
						Name:      "get",
						ArgsUsage: "first arg is the tags name - if none is set every tag will be asked for its time and config",
						Flags: []cli.Flag{
							cli.StringFlag{
								Name:  "file",
								Usage: "file to output the received json to",
							},
						},
						Action: func(cCtx *cli.Context) error {
							filename := cCtx.String("file")
							req := commandinterface.NewCommandRequest(c.getTopicByAddressAndCommand(cCtx, "get"), nil)
							return c.handleComms(req, filename)
						},
						Subcommands: []cli.Command{
							{
								Name: "time",
								Flags: []cli.Flag{
									cli.StringFlag{
										Name:  "address",
										Usage: "address to query a specific tag",
									},
								},
								Action: func(cCtx *cli.Context) error {
									req := commandinterface.NewCommandRequest(c.getTopicByAddressAndCommand(cCtx, "get_time"), nil)
									return c.handleComms(req, "")
								},
							},
							{
								Name: "config",
								Flags: []cli.Flag{
									cli.StringFlag{
										Name:  "address",
										Usage: "address to query a specific tag",
									},
								},
								Action: func(cCtx *cli.Context) error {
									logrus.Infoln("getting config")
									req := commandinterface.NewCommandRequest(c.getTopicByAddressAndCommand(cCtx, "get_config"), nil)
									return c.handleComms(req, "")
								},
							},
							{
								Name: "acceleration_log",
								Flags: []cli.Flag{
									cli.StringFlag{
										Name:  "address",
										Usage: "address to query a specific tag",
									},
								},
								Action: func(cCtx *cli.Context) error {
									logrus.Infoln("getting acceleration log")
									req := commandinterface.NewCommandRequest(c.getTopicByAddressAndCommand(cCtx, "get_acceleration_log"), nil)
									return c.handleComms(req, "")
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
