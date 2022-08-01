from torch import addr
from gatewayn.tag.tag import Tag
from bleak.backends.device import BLEDevice
from typing_extensions import Self

class TagBuilder:
    def __init__(self) -> None:
        self.tag_bleDevice = None
        self.tag_name = ""
        self.tag_address = ""

    def from_device(self, device: BLEDevice) -> Self:
        self.tag_bleDevice: BLEDevice = device
        self.tag_name = device.name
        self.tag_address = device.address
        return self

    def name(self, name: str = "") -> Self:
        self.tag_name = name
        return self

    def address(self, address: str = "") -> Self:
        self.tag_address = address
        return self

    def ble_device(self, ble_device: BLEDevice) -> Self:
        self.tag_bleDevice = ble_device
        return self

    def build(self) -> Tag:
        tag = Tag(name=self.tag_name, address=self.tag_address, device=self.ble_device)
        return tag