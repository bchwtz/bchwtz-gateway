class MqttMainfluxComm:
    def __init__(self, thing_id, thing_key):
        self.thing_id = thing_id
        self.thing_key = thing_key

    def pub(self,thing_id, thing_key,channel_id,messages):
        pass

    def sub(self, channel_id,thing_key,thing_id):
        pass