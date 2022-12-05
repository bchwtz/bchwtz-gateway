"""This demo shows the necessary steps for getting the acceleration_log from your tag."""

import asyncio
import json
import os
from gateway.config import Config
from gateway.hub.hub import Hub

def get_stream_data():
    """Connecting to a tag to grab the acceleration data.
    The first step is always to create a new asyncio eventloop in which the whole communication will be handled. On the mainloop the run_until_complete method gets called and this method gets the hub.discover_tags() callback, with a 5-second timeout as parameter.
    When all the tags in the area are discovered, one of them get selected by the MAC-adress you provide.
    This demo show you all the necessary steps and calls to get the acc_log from the hardware tag.
    """
    # creating a new hub
    hub = Hub()
    # creating a new event_loop
    main_loop = asyncio.get_event_loop()
    # discover new tags
    main_loop.run_until_complete(hub.discover_tags())
    print(hub.tags)
    if len(hub.tags) < 1:
        print("sorry - no tags discovered")
        os.Exit(0)
    # select the tag with the given adress.
    tag = hub.get_tag_by_address('C1:FC:9B:69:04:8B')
    # get the tags config - important to be able to decode the messages from the tag
    main_loop.run_until_complete(tag.get_config())
    print(tag.config.get_props())
    # get the log
    main_loop.run_until_complete(tag.activate_streaming_mode())
    # generate a json string
    # output file
    tag_json = json.dumps(hub, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4)

    # Using a context-manger to write the json-log to a file.
    with open("demos/acceleration_log.json", "w") as json_file:
        json_file.write(tag_json)

if __name__ == '__main__':
    get_stream_data()
