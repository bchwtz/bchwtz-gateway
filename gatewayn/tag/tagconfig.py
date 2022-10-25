from random import sample

from gatewayn.config import Config
import logging


class TagConfig(object):
    """ This is the configuration of the tag. The last known configuration will be saved in this shadow-class. If you alter any values of this class and want them to be recognized by the tag, call its method "set_config".
    """

    def __init__(self) -> None:
        """ Initializes a new object of type TagConfig
        """
        self.samplerate: int = 0
        self.resolution: int = 0
        self.scale: int = 0
        self.dsp_function: int = 0
        self.dsp_parameter: int = 0
        self.mode: str = ""
        self.divider: int = 0
        self.logger = logging.getLogger("TagConfig")
        self.logger.setLevel(logging.INFO)

    def set_samplerate(self, samplerate: int) -> None:
        """ Sets the tag's samplerate.
            Arguments:
                samplerate: The rate.
        """
        if samplerate not in Config.AllowedValues.samplerate.value:
            self.logger.error("defined samplerate not allowed")
            return
        self.samplerate = samplerate

    def set_resolution(self, resolution: int) -> None:
        """ Sets the tag's resolution
            Arguments:
                resolution: The resolution.
        """
        if resolution not in Config.AllowedValues.sample_resolution.value:
            self.logger.error("defined samplerate not allowed")
            return
        self.resolution = resolution

    def set_scale(self, scale: int) -> None:
        """ Sets the tag's scale:
            Arguments:
                scale: The scale.
        """
        if scale not in Config.AllowedValues.scale.value:
            self.logger.error("defined scale not allowed")
            return
        self.scale = scale

    def set_divider(self, divider: int) -> None:
        """ Sets the tag's divider (be careful using this number - it will greatly effect the performance and battery usage).
            Arguments:
                divider: divides the samplerate to reach more accurate samplerates
        """
        if divider > 254 or divider < 0:
            self.logger.error("divider is too big or too small (0-254)")
            return
        self.divider = divider

    def get_props(self) -> dict:
        """ Serializable representation of this type.
            Returns:
                Self as a dict
        """
        return {'samplerate': self.samplerate, 'resolution': self.resolution, 'scale': self.scale, 'mode': self.mode, 'divider': self.divider, 'dsp_function': self.dsp_function, 'dsp_parameter': self.dsp_parameter}