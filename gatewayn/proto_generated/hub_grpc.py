import purerpc
from . import hub_pb2 as hub__pb2
from . import tag_pb2 as tag__pb2


class HubServicer(purerpc.Servicer):
    async def StartAdvertisementScanning(self, input_message):
        raise NotImplementedError()

    async def GetTags(self, input_message):
        raise NotImplementedError()

    @property
    def service(self) -> purerpc.Service:
        service_obj = purerpc.Service(
            "gateway.Hub"
        )
        service_obj.add_method(
            "StartAdvertisementScanning",
            self.StartAdvertisementScanning,
            purerpc.RPCSignature(
                purerpc.Cardinality.UNARY_UNARY,
                hub__pb2.HubCommand,
                hub__pb2.HubResponse,
            )
        )
        service_obj.add_method(
            "GetTags",
            self.GetTags,
            purerpc.RPCSignature(
                purerpc.Cardinality.UNARY_UNARY,
                hub__pb2.GetTagRequest,
                hub__pb2.GetTagResponse,
            )
        )
        return service_obj


class HubStub:
    def __init__(self, channel):
        self._client = purerpc.Client(
            "gateway.Hub",
            channel
        )
        self.StartAdvertisementScanning = self._client.get_method_stub(
            "StartAdvertisementScanning",
            purerpc.RPCSignature(
                purerpc.Cardinality.UNARY_UNARY,
                hub__pb2.HubCommand,
                hub__pb2.HubResponse,
            )
        )
        self.GetTags = self._client.get_method_stub(
            "GetTags",
            purerpc.RPCSignature(
                purerpc.Cardinality.UNARY_UNARY,
                hub__pb2.GetTagRequest,
                hub__pb2.GetTagResponse,
            )
        )