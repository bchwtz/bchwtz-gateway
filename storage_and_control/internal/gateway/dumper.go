package gateway

import (
	"encoding/json"
	"os"

	"github.com/bchwtz/bchwtz-gateway/storage_and_control/internal/model"
	"github.com/joho/godotenv"
	"github.com/sirupsen/logrus"
	"github.com/systematiccaos/going-forward/db"
	"github.com/systematiccaos/going-forward/mqtt"
)

// manages the database and MQTT-functions for the dumping-service
type GatewayDumper struct {
	gateway
	database *db.Database
}

// creates a new dumper object
func NewDumper() GatewayDumper {
	gw := GatewayDumper{}
	gw.run()
	return gw
}

// loop to run the gateway-dumper-service
func (gw *GatewayDumper) run() {
	gw.mqclient = mqtt.Client{}
	if err := godotenv.Load("../.env"); err != nil {
		logrus.Errorln(err)
	}
	gw.ConnectMongo()
	donech := make(chan bool)
	gw.mqclient.Connect(os.Getenv("MQTT_BROKER")+":"+os.Getenv("MQTT_PORT"), os.Getenv("MQTT_CLIENTID"), os.Getenv("MQTT_USER"), os.Getenv("MQTT_PASSWORD"), true)
	gw.get_advertisement_channel = make(chan mqtt.MQTTSubscriptionMessage)
	gw.hub = model.Hub{}
	gw.listenAdvertisements()
	gw.listenLogs()
	go gw.writeAdvertisementsToDB()
	<-donech
}

// listens for advertisements on MQTT-topic and sends them to the internal get_advertisement_channel
func (gw *GatewayDumper) listenAdvertisements() {
	topic := os.Getenv("TOPIC_LISTEN_ADV")

	if err := gw.mqclient.Subscribe(topic, gw.get_advertisement_channel); err != nil {
		logrus.Fatalln(err)
	}
	logrus.Infoln("subscribing on topic " + topic)
}

// listens for new messages on the logs MQTT-topic and sends them to the internal get_advertisement_channel
func (gw *GatewayDumper) listenLogs() {
	topic := os.Getenv("TOPIC_LOG")

	if err := gw.mqclient.Subscribe(topic, gw.get_advertisement_channel); err != nil {
		logrus.Fatalln(err)
	}
	logrus.Infoln("subscribing to logs on topic " + topic)
}

// writes received advertisements to mongo
func (gw *GatewayDumper) writeAdvertisementsToDB() {
	for {
		adv, more := <-gw.get_advertisement_channel
		if !more {
			return
		}
		msgbt := adv.Message.Payload()
		logrus.Traceln(string(msgbt))
		if err := json.Unmarshal(msgbt, &gw.hub); err != nil {
			logrus.Fatalln(err)
			continue
		}
		logrus.Traceln(gw.hub.Tags)
		// we want to match the tags by address, which is already a unique identifier
		gw.database.Save(&gw.hub.Tags, "address")
		adv.Message.Ack()
	}
}

// establishes the connection to the mongodb and saves the resulting connection object in its internal gateway struct
func (gw *GatewayDumper) ConnectMongo() {
	db, err := db.ConnectMongo()
	if err != nil {
		logrus.Fatalln(err)
	}
	gw.database = db
}
