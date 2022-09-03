import logging
import gatewayn.proto_generated.hub_pb2_grpc as hub_service
import gatewayn.proto_generated.hub_pb2 as hub_messages
import grpc
from gatewayn.hub.hub import Hub
import asyncio

class HubService(hub_service.HubServicer):

    def __init__(self, hub: Hub):
        self.hub = hub

    def StartAdvertisementScanning(self, request, context):
        logging.debug(request, context)
        asyncio.get_event_loop().add_task(self.hub.listen_for_advertisements())
        res = hub_messages.HubResponse()
        return res

