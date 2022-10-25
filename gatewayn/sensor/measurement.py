class Measurement(object):
    """An object of this class creates a digital representation of a measurement. Every 
    measurement has measurements of a defined class.

    :type sensor: sensor.sensor.Sensor
    """
    def get_props(self):
        return self.__dict__