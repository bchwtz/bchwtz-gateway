"""This demo shows how to get the currently set hearbeat from the tag."""
import asyncio
from gatewayn.hub.hub import Hub

def get_tag_heatbeat()
    """This demo shows how to get the currently set hearbeat from the tag.

    The first step is always to create a new asyncio eventloop in which the whole communication will be handled.
    On the mainloop the run_until_complete method gets called and this method gets the hub.discover_tags() callback, with a 5-second timeout as parameter.
    When all the tags in the area are discovered, one of them get selected by the MAC-adress you provide.
    """
    hub = Hub()
    main_loop = asyncio.get_event_loop()
    main_loop.run_until_complete(hub.discover_tags(5))
    my_tag = hub.get_tag_by_address('CA:A5:49:28:D8:87')
    for i in range(10):
        main_loop.run_until_complete(my_tag.get_heartbeat())
        #main_loop.run_until_complete(my_tag.get_heartbeat())
        #main_loop.run_until_complete(my_tag.set_heartbeat(1001))
        #main_loop.run_until_complete(my_tag.get_heartbeat())

if __name__ == '__main__':
    get_tag_heatbeat()
