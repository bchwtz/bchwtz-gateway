from logging import Logger
import logging
import struct
from time import time
from gatewayn.config import Config
from gatewayn.tag.tagconfig import TagConfig


class Encoder():
    def __init__(self) -> None:
        self.logger: Logger = logging.getLogger("Encoder")
        self.logger.setLevel(logging.INFO)
    
    def encode_config(self, config: TagConfig) -> bytearray:
        pass

    def encode_time(self, time: float = None) -> str:
        now = struct.pack("<Q", int(time * 1000)).hex()
        command= Config.Commands.set_tag_time_substr.value + now
        self.logger.info("Set sensor time {}".format(command))
        return command