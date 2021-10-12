import paho.mqtt.client as mqtt


def on_message(client, userdata, message):
    """Wrapper for the paho on_message function.

    This is an implementation of a callback which differentiates from which
    channel the message came. In this case the callback differentiates between messages from the
    channel "messages" and every other channel.
    If the received message was published in the "messages"-Channel the call just prints a statement
    into the console.
    If the message was published in any other channel the message is printed into the console.
    """
    if str(message.topic == 'messages'):
        print('Höre Message Channel zu')

    else:
        print("Received message '" + str(message.payload) + "' on topic '"
              + message.topic + "' with QoS " + str(message.qos))


def on_disconnect(client, userdata, rc):
    """Reconnects the thing to the broker if the disconnect happened on accident.
    """
    if rc != 0:
        client.reconnect()
        return "Unexpected disconnection."


def on_publish(client, userdata, result):
    """Prints out a statement, if the publishing of a message was successful."""
    print("data published \n")


def on_connect(client, userdata, flags, rc):
    """Prints out the result code when a thing is connected to a broker."""
    # client.subscribe("channels/d580cbe3-251b-4588-86d7-a446b8eee92b/messages", qos=0)
    print("Connected with result code " + str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    """Prints the userdata and mid if the ting connects to a channel."""
    print(userdata, mid)


class Thing:
    """
    A class that represents a thing from mqtt.

    The is a wrapper for certain functions of the phao.mqtt module regarding things.
    A thing in mqtt can be a sensor for example. This sensor need to publish its data
    to a broker.
    This class aims to make it easy create a new client, and publish messages to the
    broker.

    Methods
    connect_to_broker(address)
    set_username_userpassword(username, password)
    pub_to_channel(topic, payload)
    disconnect_from_broker()
    reset_to_factory()

    """

    def __init__(self, username, password):
        """Creates a new phao-client."""
        # self.thing_id = thing_id
        # self.thing_key = thing_key
        self.client = mqtt.Client(client_id='', clean_session=True, userdata=None, transport='tcp')
        self.client.username_pw_set(username=username, password=password)
        # Setting my own callbacks.
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_message = on_message
        self.client.on_publish = on_publish
        self.client.on_subscribe = on_subscribe
        self.address = ''

    def connect_to_broker(self, address: str):
        """Wrapper for the paho connect method.

        Connects the thing to the broker. Then calls the phao loop_start-method.

        Args
        address: str
            Hostname or ip of the broker
        """
        self.address = address
        self.client.connect(address)
        self.client.loop_start()

    def pub_to_channel(self, topic: str, payload: str, subtopic=None):
        """Wrapper for the paho publish method.

        Causes the message to be published to a broker and all from there to be send to all devices subscribed to it.

        Args
        topic: str
            The topic/channel the message should be published to
        payload: str
            The contents of the message
        subtopic: str
            Potential subtopic for a channel. Defaults to None.
        """
        if subtopic is not None:
            topic += "/" + subtopic
        return self.client.publish(topic=topic, payload=payload)

    def disconnect_from_broker(self):
        """Wrapper for the phao disconnect method.

        Disconnects the client/Thing from the broker.
        """
        self.client.disconnect()

    def sub_to_channel(self, topic, qos):
        """Wrapper for the paho subscribe method.

            Subscribe the client to one or more topics.

            Args
                topic: The Topic to which to subscribe
                qos: Quality of service level default = 0
        """
        return self.client.subscribe(topic, qos=0)

    def reset_to_factory(self):
        """Wrapper for the paho reinitialise method

        resets the client/Thing to its starting state i.e. as if it was freshly created."""
        self.client.reinitialise()
