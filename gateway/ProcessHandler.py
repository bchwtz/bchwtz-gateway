"""
Multithread to handle the libraries

1. Running the MQTT Bridge on a seperated thread
2. Run the sensor connection on a seperated thread

Open Topics:
    - Comands should be defined in a seperate config file.
    - Tags IDs should not be used.
    - The job queue is probably wrong.
    - Nothing is tested so far!
"""
import logging
import threading
import time
from queue import Queue
import json
import AdvertisementLogging
import SensorGatewayBleak
from Thing import Thing
import MessageObjects
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

# Command queue for FIFO execution
ComQueue = Queue()



def read_mainflux_conf(abs_path = "gateway/mfconf.yml"):
    """
    Read the Mainflux-Configuration-File to get the communication 
    specifications.
    
    :Parameters:
        
    abs_path : TYPE, optional
       Expects the absolute path of the YML-File . The default is "".

    :Returns:
        
    mf_conf : TYPE
        Returns the configuration file as list of dictionaries.

    """
    with open(abs_path, "r") as ymlfile:
        mf_conf = yaml.load(ymlfile)
    return mf_conf
    

class thread_mqttlistener(threading.Thread):
    
    def __init__(self, threadID, name, mf_conf_file):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.logger = logging.getLogger('ProcessHandlerMF.thread_mqttlistener')
        self.logger.info("mqttlistener initialized")
        self.latesttimestamp = 0
        self.host = mf_conf_file['mf_loging']['host_url']
        self.user = mf_conf_file['mf_loging']['username']
        self.key = mf_conf_file['mf_loging']['pwd']
        self.channel = mf_conf_file['channel_specs']['command_chl']
        
    def run(self):
        mqtt_communicator = Thing(self.user, self.key)
        mqtt_communicator.connect_to_broker(self.host)
        listen_topic = 'channel'+str('/') + self.channel + str('/') + 'messages'
        msg = mqtt_communicator.listen_to_channel(listen_topic)
        self.logger.info("start listening...")
        while True: 
            if msg.timestamp > self.latesttimestamp:
                self.logger.info("new massage detected")
                self.latesttimestamp = msg.timestamp
                ComQueue.put(msg)
            if GentlyInterrupt.is_set():
                self.logger.info('MQTT Listener thread closed')   
                break
    
            
class thread_mqttwriter(threading.Thread):
    
    def __init__(self, threadID, name, mf_conf_file):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.logger = logging.getLogger('ProcessHandlerMF.thread_mqttwriter')
        self.logger.info("mqttwriter initialized")
        self.SensorObj = SensorGatewayBleak.RuuviTagAccelerometerCommunicationBleak()
        self.host = mf_conf_file['mf_loging']['host_url']
        self.user = mf_conf_file['mf_loging']['username']
        self.key = mf_conf_file['mf_loging']['pwd']
        self.advertisement_chl = mf_conf_file['channel_specs']['advertisement_chl']
        self.com_feedback_chl = mf_conf_file['channel_specs']['com_feedback_chl']

        
    def JSONGenerator(message, channel):
        MQTTBridge.sentMessage(json.dump(message))
        
        
    def run(self):
        mqtt_publisher = Thing(self.user, self.key)
        mqtt_publisher.connect_to_broker(self.host)
        advertisement_topic = 'channel'+str('/') + self.advertisement_chl + str('/') + 'messages'
        com_feedback_topic = 'channel'+str('/') + self.com_feedback_chl + str('/') + 'messages'
        while True:
            if ComQueue.empty():
                adv_msg = AdvertisementLogging.start_advertisement_logging()
                M
                self.JSONGenerator(adv_msg)
                self.logger.info('Advertisements sent to Mainflux')
            if not ComQueue.empty():
                self.SensorObj.connect_to_mac_command()


if __name__ == '__main__':
    try:
        threadListener = thread_mqttlistener(1, "Listennerthread")
        threadWriter = thread_mqttwriter(2, "Writerthread")
        threadListener.start()
        Log_ProcessHandlerMF.info('Start MQTTListener successfull')
        threadWriter.start()
        Log_ProcessHandlerMF.info('Start MQTTWriter sccessfull')
    except KeyboardInterrupt:
        GentlyInterrupt.set()
        threadWriter.join()
        threadListener.join()
        Log_ProcessHandlerMF.info('Shutdown threads successfull')
    

