package cmd

import (
	"context"

	pb "github.com/bchwtz/bchwtz-gateway/client/generated"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type Command int

var clientInstance *Client

const (
	StartAdvertisementScanning Command = 1
	GetTags                    Command = 2
)

type Client struct {
	Address        string
	Conn           *grpc.ClientConn
	GClient        pb.HubClient
	Poolsize       int
	CommandChannel chan Command
	DoneCH         chan bool
}

func (client *Client) Connect() {
	var opts []grpc.DialOption
	opts = append(opts, grpc.WithTransportCredentials(insecure.NewCredentials()))
	conn, err := grpc.Dial("[::]:50051", opts...)
	if err != nil {
		logrus.Fatalln(err)
	}

	client.GClient = pb.NewHubClient(conn)
	client.CommandChannel = make(chan Command)
	go client.runCommands()
	// <-client.DoneCH
	// res, err := client.GClient.StartAdvertisementScanning(context.Background(), &pb.HubCommand{})
	// if err != nil {
	// 	logrus.Errorln(err)
	// }
	// logrus.Println(res.String())
}

func (client *Client) runCommands() {
	for {
		cmd := <-client.CommandChannel
		switch cmd {
		case StartAdvertisementScanning:
			res, err := client.GClient.StartAdvertisementScanning(context.Background(), &pb.HubCommand{})
			if err != nil {
				logrus.Errorln(err)
			}
			logrus.Println(res.String())

		case GetTags:
			res, err := client.GClient.GetTags(context.Background(), &pb.GetTagRequest{})
			if err != nil {
				logrus.Errorln(err)
			}
			logrus.Infoln(res.Tags)
			client.DoneCH <- true
		}
	}
}

func GetInstance() *Client {
	if clientInstance == nil {
		clientInstance = &Client{
			Poolsize: 4,
		}
		clientInstance.Connect()
	}
	return clientInstance
}
