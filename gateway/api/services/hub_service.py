import logging
import queue
import gateway.proto_generated.hub_grpc as hub_service
import gateway.proto_generated.hub_pb2 as hub_messages
from google.protobuf.any_pb2 import Any
import grpc
from gateway.hub.hub import Hub
import asyncio
from typing import cast

class HubService(hub_service.HubServicer):

    def __init__(self, hub):
        self.hub = hub
        if hub is None:
            self.hub = Hub()

    async def StartAdvertisementScanning(self, context, request):
        logging.debug(request, context)
        await self.hub.listen_for_advertisements()
        res = hub_messages.HubResponse()
        return res

    async def GetTags(self, context, request):
        logging.debug(request, context)
        tags = self.hub.tags
        gtags = []
        for tag in tags:
            gtag = hub_messages.tag__pb2.Tag()
            gtag.address = tag.address
            gtag.last_seen = tag.last_seen
            if tag.config is not None:
                gtag.config.samplerate = tag.config.samplerate
                gtag.config.resolution = tag.config.resolution
                gtag.config.scale = tag.config.scale
                gtag.config.dsp_function = tag.config.dsp_function
                gtag.config.dsp_parameter = tag.config.dsp_parameter
                gtag.config.mode = tag.config.mode
            for sensor in tag.sensors:
                gsensor = hub_messages.tag__pb2.Sensor()
                gsensor.name = sensor.name
                last_measurement_any = Any()
                # TODO: fix measurements
                # if sensor.last_measurement is not None:

                    # gsensor.last_measurement.CopyFrom(sensor.last_measurement)
                # gsensor.name = sensor.name
                # gsensor.last_measurement.Pack(sensor.last_measurement)
                # for m in sensor.measurements:
                #     gsensor.measurements.append(m)
                # gtag.sensors.append(gsensor)
            gtags.append(gtag)
        res = hub_messages.GetTagResponse(tags = gtags)
        # res.tags.extend(tags)
        return res