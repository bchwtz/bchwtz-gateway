from concurrent import futures
import logging
import time
from gatewayn.api.services.hub_service import HubService
import gatewayn.proto_generated.hub_pb2_grpc as hub_service
from flask import Flask
from flask_restful import Resource, Api, reqparse
from gatewayn.hub.hub import Hub
import grpc

class API:
    def __init__(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.hub = Hub()

    def setup_routes(self):
        hub_serve = HubService(self.hub)
        hub_service.add_HubServicer_to_server(hub_serve, self.server)

    async def run(self):
        self.server.add_insecure_port('[::]:50051')
        self.server.start()
        try:
            while True:
                time.sleep(3600*24)
        except KeyboardInterrupt:
            logging.debug('GRPC stop')
            self.server.stop(0)
