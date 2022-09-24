"""This demo shows how to get the currently set hearbeat from the tag.
"""
import asyncio
from gatewayn.hub.hub import Hub

hub = Hub()
main_loop = asyncio.get_event_loop()
main_loop.run_until_complete(hub.discover_tags(5))
my_tag = hub.get_tag_by_address('CA:A5:49:28:D8:87')
for i in range(10):
    main_loop.run_until_complete(my_tag.get_heartbeat())
    #main_loop.run_until_complete(my_tag.get_heartbeat())
    #main_loop.run_until_complete(my_tag.set_heartbeat(1001))
    #main_loop.run_until_complete(my_tag.get_heartbeat())
