
import asyncio
import time
from datetime import datetime
from gateway.hub.hub import Hub
import csv
from time_functions import get_current_tag_time, set_current_tag_time


if __name__ == "__main__":
    """The Python script current_time_demo.py serves as a template for this function. 
    The tag time is requested by the helper function get_current_tag_time with the tag MAC address as parameter. 
    The results are UNIX timestamps from RuuviTag and Python before and after the tag time request. 
    All timestamps are converted to UTC and printed as a kind of log. 
    """    
    
    # get time with MAC address
    tag_time, time_now1, time_now2 = get_current_tag_time('C7:22:C6:A1:0D:DA')  
    # create list with results
    my_list = [time_now1, time_now2, tag_time, time_now1-tag_time, time_now2-tag_time]
    # append new times to csv
    with open(r'/home/pi/gateway/timedelta.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow(my_list) 
    # print get times in format %Y-%m-%d %H:%M:%S
    print('Zeiten: ',datetime.utcfromtimestamp(time_now1).strftime('%Y-%m-%d %H:%M:%S'), datetime.utcfromtimestamp(time_now2).strftime('%Y-%m-%d %H:%M:%S'), datetime.utcfromtimestamp(tag_time).strftime('%Y-%m-%d %H:%M:%S'))
