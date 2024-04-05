
import asyncio
import time
from datetime import datetime
from gateway.hub.hub import Hub
import csv


def set_current_tag_time(address):
    """The Python script current_time_demo.py serves as a template for this function. 
    It creates an asyncio event loop, searches for nearby tags with a 5 second timeout and selects a tag given by the MAC address.
    Then the time is set on the selected tag.
    """

    # create hub    
    hub = Hub()
    # create asyncio event loop
    main_loop = asyncio.get_event_loop()
    # discover all tags with a 5 second timeout
    main_loop.run_until_complete(hub.discover_tags(5))
    # get tag by mac address
    my_tag = hub.get_tag_by_address(address)

    # set time on selected tag
    main_loop.run_until_complete(my_tag.set_time())

    
def get_current_tag_time(address):
    """The Python script current_time_demo.py serves as a template for this function. 
    It creates an asyncio event loop, searches for nearby tags with a 5 second timeout and selects a tag given by the MAC address. 
    Then the actual time from the selected tag is requested. The system time of the gateway is saved before and after the time is retrieved. To ensure that the time is received and saved, a 10 second timeout is added. To get a UNIX-Timestamp, the tag time is divided by 1000.
    The Tag time and both system times will be returned.
    """    

    # create hub  
    hub = Hub()
    # create asyncio event loop
    main_loop = asyncio.get_event_loop()
    # discover all tags with a 5 second timeout
    main_loop.run_until_complete(hub.discover_tags(5))
    # get tag by mac address
    my_tag = hub.get_tag_by_address(address)

    # save system time before tag-get
    time_now1 = datetime.now().timestamp()
    # request tag time
    main_loop.run_until_complete(my_tag.get_time())
    # save system time after tag-get
    time_now2 = datetime.now().timestamp()
    
    # wait 10 seconds to ensure that the data is received
    time.sleep(10)
    
    # divide by 1000 for UNIX-Timestamp
    tag_time = my_tag.time/1000

    # return tag times 
    return tag_time, time_now1, time_now2

