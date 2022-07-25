from bleak.backends.device import BLEDevice
class Tag():
    """Hardware-object notation for a tag

    :param name: name of the tag
    :param address: full mac
    :param bleDevice: BLEDevice from bleak package
    :type Tag: gatewayn.drivers.bluetooth.bleconn.tag.Tag
    """
    def __init__(self, name: str = "", address: str = "", device: BLEDevice = None) -> None:
        self.name: str = name
        self.address: str = address
        self.bleDevice: BLEDevice = device
