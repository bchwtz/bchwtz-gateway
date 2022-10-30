# MQTT-Messages

## What is MQTT for?
MQTT is a message broking protocol for edge device messages. A message broker is a technology that takes messages from clients and delivers them to all subscribing clients for a topic. It is going to make sure all sent messages will be received by the subscribing clients. If a messages was missed out or could not be processed it can be rescheduled by the broker.  
MQTT organizes its communication in different pubsub topics that can be defined via the brokers api or simply by sending a message to a new, non-existing topic. This software is using the second approach for creating topics on MQTT. The broker used by this project is RabbitMQ with its MQTT-extension. RabbitMQ can also be used as a gateway for other message broking protocols, such as AMQP. The project uses message broking to exchange data and control commands between the different microservices.  
  
For further information please take a look at the [MQTT Essentials by HiveMQ](https://www.hivemq.com/mqtt-essentials/){:target="_blank"}

## Topic structure
The MQTT-broker has four topics by default:

* a command topic: gateway/tag/command
* a command response topic: gateway/tag/commandres
* a log topic: gateway/hub/log
* a advertisement data topic: gateway/hub/advertisements

As you are able to see the structure of the controller classes in the python-library is consistent to the topic structure in MQTT. To submit events to listening microservices new topics can be added following the same structure.  
If there is a new topic to receive the results of a streaming-command, named stream-data, the topic-name should be structured like this:  
gateway/tag/<mac_address>/stream-data  
If there are other streaming data events, they should follow the same pattern.
## Command and control interface

The command and control interface is implemented as a commandline interface in go. Its pattern is quite simple: It sends a command with a requestid as uuid to the MQTT-command topic. Next the bluetooth-gateway is going to respond to the MQTT-response topic with a response message with the requestid so the responses can be mapped to the requests.  
For further details have a look at its [implementation reference](/bchwtz-gateway/cli_ref).

## TODO
The messages should be implemented via protobuf in the future, so all code refering to the MQTT-messages can be generated automatically.