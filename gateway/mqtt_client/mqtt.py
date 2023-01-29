from paho import Client

class MQTTClient():
    """ 
        This class should manage all MQTT-Connections and reflect the internal object model to MQTT
    """
    def __init__(self):
        self.client: Client = None

    def setup_handlers():