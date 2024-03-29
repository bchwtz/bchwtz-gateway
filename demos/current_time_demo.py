
import asyncio
import time
from datetime import datetime
from gateway.hub.hub import Hub

def get_current_tag_time():
    """This script demonstrates how get and set the system time on your tag.
    
    The first step is always to create a new asyncio eventloop in which the whole communication will be handled.
    On the mainloop the run_until_complete method gets called and this method gets the hub.discover_tags() callback, with a 5-second timeout as parameter.
    When all the tags in the area are discovered, one of them get selected by the MAC-adress you provide.
    
    In this demo you set the system time on the tag to the current time when running this script.
    Immediatly afterwards the time is read from the tag.
    Then the drift between setting the time on the tag and the time which should have been set is calculated.
    """
    hub = Hub()
    main_loop = asyncio.get_event_loop()
    main_loop.run_until_complete(hub.discover_tags(5))
    my_tag = hub.get_tag_by_address('CA:A5:49:28:D8:87')

    # Setting time to current time
    time_now = datetime.now().timestamp()
    # If no time is provided the methods creates the current time stamp.
    main_loop.run_until_complete(my_tag.set_time())
    # Checking, if current time is set.
    main_loop.run_until_complete(my_tag.get_time())
    time.sleep(20)
    tag_time = my_tag.time
    print(f'time_now: {time_now}')
    print(f'tag_time: {tag_time}')
    td = tag_time - time_now
    print(td)

    print(datetime.utcfromtimestamp(td).strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    get_current_tag_time
