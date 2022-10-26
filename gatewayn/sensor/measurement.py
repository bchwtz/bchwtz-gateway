class Measurement(object):
    """An object of this class creates a digital representation of a measurement. Every 
        measurement has measurements of a defined class.
    """
    def get_props(self) -> dict:
        """ Returns the object as a dict to make it serializable.
            Returns:
                self as dict
        """
        return self.__dict__