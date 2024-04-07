
import asyncio
import time
from datetime import datetime
from gateway.hub.hub import Hub
import csv
from time_functions import get_current_tag_time, set_current_tag_time

if __name__ == "__main__":
    """The Python script current_time_demo.py serves as a template for this function. 
    The tag time is set by the helper function set_current_tag_time with the tag MAC address as parameter. 
    The set time is converted to UTC and printed as a kind of log. 
    """ 

    # set time with MAC address
    set_current_tag_time('C7:22:C6:A1:0D:DA')
    # print set time in format %Y-%m-%d %H:%M:%S
    print('set time: ',datetime.utcfromtimestamp(datetime.now().timestamp()).strftime('%Y-%m-%d %H:%M:%S'))
    
