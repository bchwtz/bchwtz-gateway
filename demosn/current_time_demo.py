"""In this demo you set the system time on the tag to the current time when running this script.
Immediatly afterwards the time read from the tag.
Then the drift between setting the time on the tag and the time which should have been set is calculated."""
import asyncio
import time
from datetime import datetime
from gatewayn.hub.hub import Hub

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