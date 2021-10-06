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
try:
    import MQTTBridge
except:
    print('MQTTBridge could not be imported!')
import AdvertisementLogging
import SensorGatewayBleak

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

class thread_mqttlistener(threading.Thread):
    
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.logger = logging.getLogger('ProcessHandlerMF.thread_mqttlistener')
        self.logger.info("mqttlistener initialized")
        self.latesttimestamp = 0
        
    def run(self):
        self.logger.info("start listening...")
        while True:
            msg = MQTTBridge.getMessage()
            if msg.timestamp > self.latesttimestamp:
                self.logger.info("new massage detected")
                self.latesttimestamp = msg.timestamp
                ComQueue.put(msg)
            if GentlyInterrupt.is_set():
                self.logger.info('MQTT Listener thread closed')   
                break
            
class thread_mqttwriter(threading.Thread):
    
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.logger = logging.getLogger('ProcessHandlerMF.thread_mqttwriter')
        self.logger.info("mqttwriter initialized")
        self.SensorObj = SensorGatewayBleak.RuuviTagAccelerometerCommunicationBleak()
    
    def JSONGenerator(message, channel):
        MQTTBridge.sentMessage(json.dump(message))
        
        
    def run(self):
        while True:
            if ComQueue.empty():
                adv_msg = AdvertisementLogging.start_advertisement_logging()
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
    

