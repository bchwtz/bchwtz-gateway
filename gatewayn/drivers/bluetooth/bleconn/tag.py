class Tag():
    """Hardware-object notation for a tag

    :param name: name of the tag
    :param address: full mac
    :type Tag: gatewayn.drivers.bluetooth.bleconn.tag.Tag
    """
    def __init__(self, name = "", address = "") -> None:
        self.name = name
        self.address = address