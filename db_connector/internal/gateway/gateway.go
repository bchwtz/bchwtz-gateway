package gateway

import (
	"encoding/json"
	"os"

	"github.com/bchwtz-fhswf/gateway/db_connector/internal/model"
	"github.com/joho/godotenv"
	"github.com/sirupsen/logrus"
	"github.com/systematiccaos/going-forward/db"
	"github.com/systematiccaos/going-forward/mqtt"
)

type Gateway struct {
	mqclient                  mqtt.Client
	hub                       model.Hub
	get_advertisement_channel chan mqtt.MQTTSubscriptionMessage
	database                  *db.Database
}

func NewGateway() Gateway {
	gw := Gateway{}
	gw.run()
	return gw
}

func (gw *Gateway) run() {
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
	go gw.writeAdvertisementsToDB()
	<-donech
}

func (gw *Gateway) listenAdvertisements() {
	topic := os.Getenv("TOPIC_LISTEN_ADV")

	if err := gw.mqclient.Subscribe(topic, gw.get_advertisement_channel); err != nil {
		logrus.Fatalln(err)
	}
	logrus.Infoln("subscribing on channel " + topic)
}

func (gw *Gateway) writeAdvertisementsToDB() {
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

func (gw *Gateway) ConnectMongo() {
	db, err := db.ConnectMongo()
	if err != nil {
		logrus.Fatalln(err)
	}
	gw.database = db
}
