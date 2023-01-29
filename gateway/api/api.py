from concurrent import futures
import logging
import time
import asyncio
from gateway.api.services.hub_service import HubService
import gateway.proto_generated.hub_pb2 as hub_service
from gateway.hub.hub import Hub
from purerpc import Server
import grpc

class API:
    def __init__(self):
        self.server: Server = Server(50051)
        self.hub: Hub = Hub()
        self.hub_service = HubService(self.hub)

    def setup_routes(self):
        self.server.add_service(self.hub_service.service)

    async def run(self):
        asyncio.create_task(self.hub.listen_for_advertisements(5000))
        await self.server.serve_async()
        # try:
        #     while True:
        #         time.sleep(3600*24)
        # except KeyboardInterrupt:
        #     logging.debug('GRPC stop')
        #     self.server.stop(0)
