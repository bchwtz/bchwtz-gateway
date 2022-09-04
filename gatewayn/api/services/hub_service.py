import logging
import queue
import gatewayn.proto_generated.hub_grpc as hub_service
import gatewayn.proto_generated.hub_pb2 as hub_messages
import grpc
from gatewayn.hub.hub import Hub
import asyncio

class HubService(hub_service.HubServicer):

    def __init__(self, hub: Hub):
        self.hub = hub

    async def StartAdvertisementScanning(self, context, request):
        logging.debug(request, context)
        await self.hub.listen_for_advertisements()
        res = hub_messages.HubResponse()
        return res

    async def GetTags(self, context, request):
        logging.debug(request, context)
        tags = self.hub.tags
        res = hub_messages.GetTagResponse()
        res.tags = tags
        return res