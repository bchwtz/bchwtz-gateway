import struct
import time
from gateway.sensor.SensorConfigEnum import SamplingRate, SamplingResolution,MeasuringRange
import logging
import yaml
import os.path
#import os
# Look to the path of your current working directory
#working_directory = os.getcwd()

log=logging.getLogger("msg")
"""
This region is used to wrap the returned values of the sensor into an object
"""
#try:
with open(os.path.dirname(__file__)+ '/../communication_interface.yml') as ymlfile:
    sensor_interface = yaml.safe_load(ymlfile)
#except Exception:
#    print(working_directory)
#    print("error")

# %% Recieved msg objects from sensor
class return_values_from_sensor(object):
    def __init__(self,returnValue=None):
        """
        

        Parameters
        ----------
        returnValue : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        if returnValue is not None:
            self.returnValue=returnValue
            print(self.returnValue)
        else:
            self.returnValue=""


    @classmethod
    def from_get_config(cls, status, sample_rate, resolution, scale, dsp_function, dsp_parameter, mode,divider, mac):
        """
        

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        status : TYPE
            DESCRIPTION.
        sample_rate : TYPE
            DESCRIPTION.
        resolution : TYPE
            DESCRIPTION.
        scale : TYPE
            DESCRIPTION.
        dsp_function : TYPE
            DESCRIPTION.
        dsp_parameter : TYPE
            DESCRIPTION.
        mode : TYPE
            DESCRIPTION.
        divider : TYPE
            DESCRIPTION.
        mac : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        reval=config_Object(status, sample_rate, resolution, scale, dsp_function, dsp_parameter, mode,divider, mac)
        return cls(reval)

    @classmethod
    def from_get_time(cls, status, recieved_time, mac):
        """
        

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        status : TYPE
            DESCRIPTION.
        recieved_time : TYPE
            DESCRIPTION.
        mac : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        reval=time_Object(status, recieved_time,mac)
        print("got Time")
        return cls(reval)

    @classmethod
    def from_get_flash_statistics(cls,  logging_status, ringbuffer_start, ringbuffer_end, mac,
                                  ringbuffer_size, valid_records, dirty_records, words_reserved, words_used,
                                  largest_contig,
                                  freeable_words):
        """
        

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        logging_status : TYPE
            DESCRIPTION.
        ringbuffer_start : TYPE
            DESCRIPTION.
        ringbuffer_end : TYPE
            DESCRIPTION.
        mac : TYPE
            DESCRIPTION.
        ringbuffer_size : TYPE
            DESCRIPTION.
        valid_records : TYPE
            DESCRIPTION.
        dirty_records : TYPE
            DESCRIPTION.
        words_reserved : TYPE
            DESCRIPTION.
        words_used : TYPE
            DESCRIPTION.
        largest_contig : TYPE
            DESCRIPTION.
        freeable_words : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        reval = flash_statistics_Object(  logging_status, ringbuffer_start, ringbuffer_end, mac,
                                  ringbuffer_size, valid_records, dirty_records, words_reserved, words_used,
                                  largest_contig,
                                  freeable_words)
        return cls(reval)
    @classmethod
    def form_get_status(cls, status,mac):
        """
        

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        status : TYPE
            DESCRIPTION.
        mac : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        reval=status_object(status,mac)
        print(reval)
        return cls(reval)

    @classmethod
    def from_get_accelorationdata(cls,accelorationdata,mac):
        """
        

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        accelorationdata : TYPE
            DESCRIPTION.
        mac : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        reval=acceloration_data_Object(accelorationdata,mac)
        return cls(reval)
    @classmethod
    def from_get_advertisementdata(cls,advertisementData, mac, time):
        """
        

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        advertisementData : TYPE
            DESCRIPTION.
        mac : TYPE
            DESCRIPTION.
        time : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        reval=advertisement_data_Object(advertisementData,mac,time)
        return cls(reval)


class time_Object(object):
    def __init__(self,status, recieved_time,mac):
        """
        

        Parameters
        ----------
        status : TYPE
            DESCRIPTION.
        recieved_time : TYPE
            DESCRIPTION.
        mac : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.status = status
        self.recieved_time = recieved_time
        self.mac = mac

class config_Object(object):
    def __init__(self, status, sample_rate, resolution, scale, dsp_function, dsp_parameter, mode, divider, mac):
        """
        

        Parameters
        ----------
        status : TYPE
            DESCRIPTION.
        sample_rate : TYPE
            DESCRIPTION.
        resolution : TYPE
            DESCRIPTION.
        scale : TYPE
            DESCRIPTION.
        dsp_function : TYPE
            DESCRIPTION.
        dsp_parameter : TYPE
            DESCRIPTION.
        mode : TYPE
            DESCRIPTION.
        divider : TYPE
            DESCRIPTION.
        mac : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

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
        """
        

        Parameters
        ----------
        logging_status : TYPE
            DESCRIPTION.
        ringbuffer_start : TYPE
            DESCRIPTION.
        ringbuffer_end : TYPE
            DESCRIPTION.
        mac : TYPE
            DESCRIPTION.
        ringbuffer_size : TYPE
            DESCRIPTION.
        valid_records : TYPE
            DESCRIPTION.
        dirty_records : TYPE
            DESCRIPTION.
        words_reserved : TYPE
            DESCRIPTION.
        words_used : TYPE
            DESCRIPTION.
        largest_contig : TYPE
            DESCRIPTION.
        freeable_words : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

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
        """
        

        Parameters
        ----------
        status : TYPE
            DESCRIPTION.
        mac : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

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
        """
        

        Parameters
        ----------
        accelorationData : TYPE
            DESCRIPTION.
        mac : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.loggingData=list(map(list, zip(accelorationData[0], accelorationData[1], accelorationData[2],
                           accelorationData[3])))
        self.mac=mac

class advertisement_data_Object(object):
    def __init__(self, advertisementData,mac, time):
        """
        

        Parameters
        ----------
        advertisementData : TYPE
            DESCRIPTION.
        mac : TYPE
            DESCRIPTION.
        time : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.advertisementData=advertisementData
        self.mac=mac
        self.time=time


#%% Send msg objects to sensor
"""
All code below is used to send messages to the sensor.
"""
class send_msg_object(object):
    #add logger
    log = log

    def __init__(self, message=None):
        """
        

        Parameters
        ----------
        message : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        if message is not None:
            print(message)
            self.message = message
            print(self.message)
        else:
            self.message = ""


    @classmethod
    def to_set_sensorTime(cls,  mac=""):
        """
        

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        mac : TYPE, optional
            DESCRIPTION. The default is "".

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # Need time as float. Use time.time() for current time.
        now=time.time()
        timestamp = struct.pack("<Q", int(now * 1000)).hex()
        command=sensor_interface['commands']['substring_set_sensor_time'] + timestamp 
        reval = send_set_sensor_time_object(mac, command)
        return cls(reval)

    @classmethod
    def to_set_sensorConfig(cls, mac="", sampling_rate='FF', sampling_resolution='FF', measuring_range='FF',
                          divider="FF"):
        """
        

        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        mac : TYPE, optional
            DESCRIPTION. The default is "".
        sampling_rate : TYPE, optional
            DESCRIPTION. The default is 'FF'.
        sampling_resolution : TYPE, optional
            DESCRIPTION. The default is 'FF'.
        measuring_range : TYPE, optional
            DESCRIPTION. The default is 'FF'.
        divider : TYPE, optional
            DESCRIPTION. The default is "FF".

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # Check if arguments are given and valid
        if sampling_rate == 'FF':
            hex_sampling_rate = 'FF'
        elif sampling_rate in SamplingRate._value2member_map_:
            hex_sampling_rate = SamplingRate(sampling_rate).name[1:]
        else:
            cls.log.warning("Wrong sampling rate")
            hex_sampling_rate = 'FF'
        # Check if arguments are given and valid
        if sampling_resolution == 'FF':
            hex_sampling_resolution = 'FF'
        elif sampling_resolution in SamplingResolution._value2member_map_:
            hex_sampling_resolution = SamplingResolution(sampling_resolution).name[1:]
        else:
            cls.log.warning("Wrong sampling resolution")
            hex_sampling_resolution = 'FF'
        # Check if arguments are given and valid
        if measuring_range == 'FF':
            hex_measuring_range = 'FF'
        elif measuring_range in MeasuringRange._value2member_map_:
            hex_measuring_range = MeasuringRange(measuring_range).name[1:]
        else:
            cls.log.warning("Wrong measuring range")
            hex_measuring_range = 'FF'
        if divider == 'FF':
            hex_divider = 'FF'
        else:
            div=""
            try:
               div= int(divider)
            except Exception as ex :
                cls.log.error(str(ex))
                cls.log.warning("Divider must be an int value")
            if isinstance(div,int):
                hex_divider =hex(div)[2:]
            else:
                hex_divider='FF'
        # Create command string and send it to targets. If some values aren't correct the defautl value "FF" is sent
        command_string = sensor_interface['commands']['substring_set_config_sensor'] + hex_sampling_rate + hex_sampling_resolution + hex_measuring_range + "FFFFFF" + hex_divider + "00"
        reval=send_set_config_object(mac=mac, command=command_string)
        return cls(reval)

    @classmethod
    def to_activate_logging(cls, mac=""):
        command= sensor_interface['commands']['activate_logging_at_sensor']
        reval=send_activate_logging_object(mac=mac, command=command)
        return cls(reval)
    @classmethod
    def to_deactivate_logging(cls, mac=""):
        command = sensor_interface['commands']['deactivate_logging_at_sensor']
        reval = send_deactivate_logging_object(mac=mac, command=command)
        return cls(reval)

    @classmethod
    def to_get_sensor_time(cls, mac=""):
        command = sensor_interface['commands']['get_time_from_sensor']
        reval = send_get_senor_time_object(mac=mac, command=command)
        return cls(reval)

    @classmethod
    def to_get_config(cls, mac=""):
        command = sensor_interface['commands']['get_config_from_sensor']
        reval = send_get_config_object(mac=mac, command=command)
        return cls(reval)

    @classmethod
    def to_get_flash_statistics(cls, mac=""):
        command = sensor_interface['commands']['get_flash_statistic']
        reval = send_get_flash_statistics_object(mac=mac, command=command)
        return cls(reval)

    @classmethod
    def to_get_logging_status(cls, mac=""):
        command = sensor_interface['commands']['get_logging_status']
        reval = send_get_logging_status_object(mac=mac, command=command)
        return cls(reval)
    @classmethod
    def to_get_acceleration_data(cls, mac=""):
        command = sensor_interface['commands']['readAllString']
        reval = send_get_acceleration_data_object(mac=mac, command=command)
        return cls(reval)

    @classmethod
    def to_activate_advertisement_logging(cls, mac=""):
        command = sensor_interface['commands']['activate_logging_at_sensor']
        reval = send_activate_advertisement_logging_object(mac=mac, command=command)
        return cls(reval)


class send_set_sensor_time_object(object):
        def __init__(self, mac, command):
            """
            

            Parameters
            ----------
            mac : TYPE
                DESCRIPTION.
            command : TYPE
                DESCRIPTION.

            Returns
            -------
            None.

            """
            self.mac=mac
            self.command=command

class send_set_config_object(object):
        def __init__(self,mac,command):
            """
            

            Parameters
            ----------
            mac : TYPE
                DESCRIPTION.
            command : TYPE
                DESCRIPTION.

            Returns
            -------
            None.

            """
            self.mac=mac
            self.command=command

class send_activate_logging_object(object):
        def __init__(self,mac, command):
            """
            

            Parameters
            ----------
            mac : TYPE
                DESCRIPTION.
            command : TYPE
                DESCRIPTION.

            Returns
            -------
            None.

            """
            self.mac=mac
            self.command=command


class send_deactivate_logging_object(object):
    def __init__(self, mac, command):
        """
        

        Parameters
        ----------
        mac : TYPE
            DESCRIPTION.
        command : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.mac = mac
        self.command = command

class send_get_config_object(object):
    def __init__(self, mac, command):
        """
        

        Parameters
        ----------
        mac : TYPE
            DESCRIPTION.
        command : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.mac = mac
        self.command = command

class send_get_senor_time_object(object):
    def __init__(self, mac, command):
        """
        

        Parameters
        ----------
        mac : TYPE
            DESCRIPTION.
        command : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.mac = mac
        self.command = command


class send_get_flash_statistics_object(object):
    def __init__(self, mac, command):
        """
        

        Parameters
        ----------
        mac : TYPE
            DESCRIPTION.
        command : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.mac = mac
        self.command = command

class send_get_logging_status_object(object):
    def __init__(self, mac, command):
        """
        

        Parameters
        ----------
        mac : TYPE
            DESCRIPTION.
        command : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.mac = mac
        self.command = command

class send_get_acceleration_data_object(object):
    def __init__(self, mac, command):
        """
        

        Parameters
        ----------
        mac : TYPE
            DESCRIPTION.
        command : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.mac = mac
        self.command = command

class send_activate_advertisement_logging_object(object):
    def __init__(self, mac, command):
        """
        

        Parameters
        ----------
        mac : TYPE
            DESCRIPTION.
        command : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.mac = mac
        self.command = command