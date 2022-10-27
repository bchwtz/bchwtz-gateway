"""
Executable Skript to start the gateway-mqtt project.
This file functioning since the restructuring of the gateway repository.
Trademarks and product names have been replaced by Sensor.
"""
import logging
import threading
import time
import settings
import json
import AdvertisementLogging
import SensorGatewayBleak
from Thing import Thing
import yaml

# %% Basic Config - Logger ------------------------------------------------------
# Creat a named logger 'ProcessHandlerMF' and set it on INFO level
Log_ProcessHandlerMF = logging.getLogger('ProcessHandlerMF')

# Create a file handler
file_handler = logging.FileHandler('ProcessHandlerMF.log')
file_handler.setLevel(logging.INFO)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
Log_ProcessHandlerMF.addHandler(file_handler)
Log_ProcessHandlerMF.addHandler(console_handler)

# Interupting Event
GentlyInterrupt = threading.Event()




def read_mainflux_conf(abs_path = "mfconf.yml"):
    """
    Read the Mainflux-Configuration-File to get the communication 
    specifications.
    
    :parameters:   
        abs_path : TYPE, optional
            Expects the absolute path of the YML-File . The default is "".

    :returns:
        
    mf_conf : TYPE
        Returns the configuration file as list of dictionaries.

    """
    with open(abs_path, "r") as ymlfile:
        mf_conf = yaml.safe_load(ymlfile)
    return mf_conf
    

class thread_mqttlistener(threading.Thread):
    """    
    This Theadclass listens to the `command_chl` (command channel).
    
    """
    def __init__(self, threadID, name, mf_conf_file):
        """
        Constructor

        :parameters:
            threadID : int
                Default input of a thread class. 
            name : str
                Default input of a thread class.
            mf_conf_file : dict
                mf_conf_file is needed to connect to the mqtt broker.
            

        :returns:
            None.

        """
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.logger = logging.getLogger('ProcessHandlerMF.thread_mqttlistener')
        self.logger.info("mqttlistener initialized")
        self.latesttimestamp = 0
        self.host = mf_conf_file['mf_login']['host_url']
        self.user = mf_conf_file['mf_login']['username']
        self.key = mf_conf_file['mf_login']['pwd']
        self.channel = mf_conf_file['channel_specs']['command_chl']
    

        
    def run(self):
        """
        Main function of this class. Class needs the `Thing` module to get connected
        to the Server. GentlyInterrupt is a thread event which is set by Keyboardinterrupt.

        :returns:
            None.

        """
        mqtt_communicator = Thing(self.user, self.key)
        mqtt_communicator.connect_to_broker(self.host)
        listen_topic = 'channels'+str('/') + self.channel + str('/') + 'messages'
        mqtt_communicator.sub_to_channel(topic=listen_topic, qos = 0)
        self.logger.info("start listening...")
        while True:
            pass
            if GentlyInterrupt.is_set():
                self.logger.info('MQTT Listener thread closed')   
                break

                
class thread_mqttAdvertisements(threading.Thread):
    """
    This threadclass handels the Advertisements.
    """
    def __init__(self, threadID, name):
        """
        Constructor

        :parameters:
            threadID : int
                Default input of a thread class. 
            name : str
                Default input of a thread class.
            mf_conf_file : dict
                mf_conf_file is needed to connect to the mqtt broker.
            

        :returns:
            None.

        """
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.logger = logging.getLogger('ProcessHandlerMF.thrad_mqttAdvertisements')
        self.logger.info("mqttwriter mqttAdvertisements")
        
    def run(self):
        """
        Calls the gateway submodule `Advertisementloggin`.
        GentlyInterrupt is a thread event which is set by Keyboardinterrupt.

        :returns:
            None.

        """
        AdvertisementLogging.advertisement_logging()
        while True:
            if GentlyInterrupt.is_set():
                self.logger.info('MQTT Listener thread closed')   
                break
            pass

            
class thread_mqttwriter(threading.Thread):
    """
    This threadclass excecuts incomming commands. 
    """
    def __init__(self, threadID, name, mf_conf_file):
        """
        Constructor

        :parameters:
            threadID : int
                Default input of a thread class. 
            name : str
                Default input of a thread class.
            mf_conf_file : dict
                mf_conf_file is needed to connect to the mqtt broker.
            

        :returns:
            None.

        """
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.logger = logging.getLogger('ProcessHandlerMF.thread_mqttwriter')
        self.logger.info("mqttwriter initialized")
        self.SensorObj = SensorGatewayBleak.SensorTagAccelerometerCommunicationBleak()
        self.host = mf_conf_file['mf_login']['host_url']
        self.user = mf_conf_file['mf_login']['username']
        self.key = mf_conf_file['mf_login']['pwd']
        self.channel = mf_conf_file['channel_specs']['command_chl']
        
        
    def run(self):
        """
        Main function of the thread class. It published the return values from `SensorGatewayBleak` to the
        com_feedback_chl onder the subtopic `feedback`.

        :returns:
            None.

        """
        mqtt_publisher = Thing(self.user, self.key)
        mqtt_publisher.connect_to_broker(self.host)   
        com_feedback_topic = 'channels' + str('/') + self.channel + str('/') + 'messages' +str('/')+'feedback'    
        
        while True:
            if not settings.ComQueue.empty():
                fb = 'Failure'
                com = settings.ComQueue.get()
                print(com)
                print('success')
                if com[0] == 'get_config_from_sensor':
                    fb = self.SensorObj.get_config_from_sensor(specific_mac=com[1])                    
                elif com[0] == 'get_time_from_sensor':
                    fb = self.SensorObj.get_time_from_sensor(specific_mac=com[1])
                elif com[0] == 'get_flash_statistic':
                    fb = self.SensorObj.get_flash_statistic(specific_mac=com[1])
                elif com[0] == 'get_logging_status':
                    fb = self.SensorObj.get_logging_status(specific_mac=com[1])
                mqtt_publisher.pub_to_channel(topic= com_feedback_topic, payload = json.dumps(fb)) 
                #print('published')
                time.sleep(5)

if __name__ == '__main__':
    """
    This Skript can be called via commandline and can by killd via keyboardinterrupt
    """
    settings.init()
    Log_ProcessHandlerMF.info("Global command queue initialized")
    connection_specs = read_mainflux_conf()
    Log_ProcessHandlerMF.info("Connection specifications loaded...")
    UserIn = input("Press Enter to start Threads...")
    try:
        threadListener = thread_mqttlistener(1, "Listennerthread", connection_specs)
        threadWriter = thread_mqttwriter(2, "Writerthread", connection_specs)
        threadAdv = thread_mqttAdvertisements(3, "AdvertisementsThread")
        threadListener.start()
        Log_ProcessHandlerMF.info('Start MQTTListener successfull')
        threadWriter.start()
        Log_ProcessHandlerMF.info('Start MQTTWriter sccessfull')
        threadAdv.start()
        Log_ProcessHandlerMF.info('Start MQTTAdvertisements sccessfull')
    except KeyboardInterrupt:
        GentlyInterrupt.set()
        threadWriter.join()
        threadListener.join()
        threadAdv.join()
        Log_ProcessHandlerMF.info('Shutdown threads successfull')
