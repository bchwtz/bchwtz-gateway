"""
This module was used to create a dictionary of the values returned 
by a spicific sensor. The dictionary can then by converted into a json object,
to send it to a backend like influx or mainflux.
"""
import logging

log = logging.getLogger("msg")
"""
This region is used to wrap the returned values of the sensor into an object
"""

# %% received msg objects from sensor
class return_values_from_sensor(object):
    def __init__(self,returnValue=None):
        """This class is used to create a standard
        dictionary of return values.

        :param returnValue: [description], defaults to None
        :type returnValue: [type], optional
        """
        if returnValue is not None:
            self.returnValue=returnValue
            print(self.returnValue)
        else:
            self.returnValue=""


    @classmethod
    def from_get_config(cls, status, sample_rate, resolution, scale, dsp_function, dsp_parameter, mode,divider, mac):
        """Classmethod to parse the get_config() return values.

        :param status: [description]
        :type status: [type]
        :param sample_rate: [description]
        :type sample_rate: [type]
        :param resolution: [description]
        :type resolution: [type]
        :param scale: [description]
        :type scale: [type]
        :param dsp_function: [description]
        :type dsp_function: [type]
        :param dsp_parameter: [description]
        :type dsp_parameter: [type]
        :param mode: [description]
        :type mode: [type]
        :param divider: [description]
        :type divider: [type]
        :param mac: [description]
        :type mac: [type]
        :return: [description]
        :rtype: [type]
        """
        reval=config_Object(status, sample_rate, resolution, scale, dsp_function, dsp_parameter, mode,divider, mac)
        return cls(reval)

    @classmethod
    def from_get_time(cls, status, received_time, mac):
        """Classmethod to parse the get_time() return values.

        :param status: [description]
        :type status: [type]
        :param received_time: [description]
        :type received_time: [type]
        :param mac: [description]
        :type mac: [type]
        :return: [description]
        :rtype: [type]
        """
        reval=time_Object(status, received_time,mac)
        print("got Time")
        return cls(reval)

    @classmethod
    def from_get_flash_statistics(cls,  logging_status, ringbuffer_start, ringbuffer_end, mac,
                                  ringbuffer_size, valid_records, dirty_records, words_reserved, words_used,
                                  largest_contig,
                                  freeable_words):
        """Classmethod to parse the get_flash_statistics() return values.

        :param logging_status: [description]
        :type logging_status: [type]
        :param ringbuffer_start: [description]
        :type ringbuffer_start: [type]
        :param ringbuffer_end: [description]
        :type ringbuffer_end: [type]
        :param mac: [description]
        :type mac: [type]
        :param ringbuffer_size: [description]
        :type ringbuffer_size: [type]
        :param valid_records: [description]
        :type valid_records: [type]
        :param dirty_records: [description]
        :type dirty_records: [type]
        :param words_reserved: [description]
        :type words_reserved: [type]
        :param words_used: [description]
        :type words_used: [type]
        :param largest_contig: [description]
        :type largest_contig: [type]
        :param freeable_words: [description]
        :type freeable_words: [type]
        :return: [description]
        :rtype: [type]
        """
        reval = flash_statistics_Object(  logging_status, ringbuffer_start, ringbuffer_end, mac,
                                  ringbuffer_size, valid_records, dirty_records, words_reserved, words_used,
                                  largest_contig,
                                  freeable_words)
        return cls(reval)

    @classmethod
    def form_get_status(cls, status,mac):
        """Classmethod to parse the get_status() return values.

        :param status: [description]
        :type status: [type]
        :param mac: [description]
        :type mac: [type]
        :return: [description]
        :rtype: [type]
        """
        reval=status_object(status,mac)
        print(reval)
        return cls(reval)

    @classmethod
    def from_get_accelorationdata(cls,accelorationdata,mac):
        """Classmethod to parse the get_accelorationdata() return values.

        :param accelorationdata: [description]
        :type accelorationdata: [type]
        :param mac: [description]
        :type mac: [type]
        :return: [description]
        :rtype: [type]
        """
        reval=acceloration_data_Object(accelorationdata,mac)
        return cls(reval)

    @classmethod
    def from_get_advertisementdata(cls,advertisementData, mac, time):
        """Classmethod to parse the get_advertisementdata() return values.

        :param advertisementData: [description]
        :type advertisementData: [type]
        :param mac: [description]
        :type mac: [type]
        :param time: [description]
        :type time: [type]
        :return: [description]
        :rtype: [type]
        """
        reval=advertisement_data_Object(advertisementData,mac,time)
        return cls(reval)


class time_Object(object):
    def __init__(self,status, received_time,mac):
        """Classmethod to parse the get_time() return values.

        :param status: [description]
        :type status: [type]
        :param received_time: [description]
        :type received_time: [type]
        :param mac: [description]
        :type mac: [type]
        """
        self.status = status
        self.received_time = received_time
        self.mac = mac

class config_Object(object):
    def __init__(self, status, sample_rate, resolution, scale, dsp_function, dsp_parameter, mode, divider, mac):
        """Class to parse the get_config() return values.

        :param status: [description]
        :type status: [type]
        :param sample_rate: [description]
        :type sample_rate: [type]
        :param resolution: [description]
        :type resolution: [type]
        :param scale: [description]
        :type scale: [type]
        :param dsp_function: [description]
        :type dsp_function: [type]
        :param dsp_parameter: [description]
        :type dsp_parameter: [type]
        :param mode: [description]
        :type mode: [type]
        :param divider: [description]
        :type divider: [type]
        :param mac: [description]
        :type mac: [type]
        """
        self.status = status
        self.sample_rate = sample_rate
        self.resolution = resolution
        self.scale = scale
        self.dsp_function = dsp_function
        self.dsp_parameter = dsp_parameter
        self.mode = mode
        self.divider=divider
        self.mac = mac

class flash_statistics_Object(object):
    def __init__(self,  logging_status, ringbuffer_start, ringbuffer_end, mac,
                                  ringbuffer_size, valid_records, dirty_records, words_reserved, words_used,
                                  largest_contig,
                                  freeable_words):
        """Class to parse the get_flash_statistic() return values.

        :param logging_status: [description]
        :type logging_status: [type]
        :param ringbuffer_start: [description]
        :type ringbuffer_start: [type]
        :param ringbuffer_end: [description]
        :type ringbuffer_end: [type]
        :param mac: [description]
        :type mac: [type]
        :param ringbuffer_size: [description]
        :type ringbuffer_size: [type]
        :param valid_records: [description]
        :type valid_records: [type]
        :param dirty_records: [description]
        :type dirty_records: [type]
        :param words_reserved: [description]
        :type words_reserved: [type]
        :param words_used: [description]
        :type words_used: [type]
        :param largest_contig: [description]
        :type largest_contig: [type]
        :param freeable_words: [description]
        :type freeable_words: [type]
        """

        self.logging_status = logging_status
        self.ringbuffer_start = ringbuffer_start
        self.ringbuffer_end = ringbuffer_end
        self.ringbuffer_size = ringbuffer_size
        self.valid_records = valid_records
        self.dirty_records = dirty_records
        self.words_reserved = words_reserved
        self.words_used = words_used
        self.largest_contig = largest_contig
        self.freeable_words = freeable_words
        self.mac = mac

class status_object(object):
    def __init__(self, status,mac):
        """Classmethod to parse the get_status() return values.

        :param status: [description]
        :type status: [type]
        :param mac: [description]
        :type mac: [type]
        """
        print("logging status")
        self.mac=mac
        if status==0:
            self.status=1
        elif status==1:
            self.status=0
        else:
            self.status=-1
        print(self.status)

class acceloration_data_Object(object):
    def __init__(self, accelorationData, mac):
        """Classmethod to parse the acceleration data.

        :param accelorationData: [description]
        :type accelorationData: [type]
        :param mac: [description]
        :type mac: [type]
        """
        self.loggingData=list(map(list, zip(accelorationData[0], accelorationData[1], accelorationData[2],
                           accelorationData[3])))
        self.mac=mac

class advertisement_data_Object(object):
    def __init__(self, advertisementData,mac, time):
        """Classmethod to parse the advertisement data.

        :param advertisementData: [description]
        :type advertisementData: [type]
        :param mac: [description]
        :type mac: [type]
        :param time: [description]
        :type time: [type]
        """
        self.advertisementData=advertisementData
        self.mac=mac
        self.time=time