package main

import (
	"context"

	pb "github.com/bchwtz-fhswf/gateway/client/generated"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func main() {
	var opts []grpc.DialOption
	opts = append(opts, grpc.WithTransportCredentials(insecure.NewCredentials()))
	conn, err := grpc.Dial("[::]:50051", opts...)
	if err != nil {
		logrus.Fatalln(err)
	}
	defer conn.Close()

	client := pb.NewHubClient(conn)
	res, err := client.StartAdvertisementScanning(context.Background(), &pb.HubCommand{})
	if err != nil {
		logrus.Errorln(err)
	}
	logrus.Println(res.String())
}
