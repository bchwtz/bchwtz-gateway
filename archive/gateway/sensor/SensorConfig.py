class SensorConfig():
    def __init__(self, sample_rate=None, resolution=None, scale=None, dsp_function=None, dsp_parameter=None, mode=None, divider=None, mac=None):
        """Storage dto for the sensor's config. It is used to store all important parameters. This config object shall be updated on each update to the sensor config itself.

        :param sample_rate: current samplerate of the sensor, defaults to None
        :type sample_rate: int, optional
        :param resolution: current resolution of the sensor, defaults to None
        :type resolution: int, optional
        :param scale: current scale of the sensor, defaults to None
        :type scale: int, optional
        :param dsp_function: current dsp function, defaults to None
        :type dsp_function: int, optional
        :param dsp_parameter: current dsp parameter, defaults to None
        :type dsp_parameter: int, optional
        :param mode: current mode of the sensor, defaults to None
        :type mode: int, optional
        :param divider: current divider of the sensor, defaults to None
        :type divider: int, optional
        :param mac: mac address of the sensor, defaults to None
        :type mac: string, optional
        """
        self.sample_rate = sample_rate
        self.resolution = resolution
        self.scale = scale
        self.dsp_funtion = dsp_function
        self.dsp_parameter = dsp_parameter
        self.mode = mode
        self.divider = divider
        self.mac = mac

    def from_dict(self, dct):
        """ Converts a dictionary with the correct key-value-set to a sensor config object.

        :param dct: [description]
        :type dct: [type]
        :return: [description]
        :rtype: [type]
        """
        for key in dct:
            setattr(self, key, dct[key])
        return self
    def __repr__(self) -> str:
        return str(self.__dict__)