from time import sleep

import asyncio
import json
import uuid
import os
from gateway.config import Config
from gateway.hub.hub import Hub

# starting out with a new hub
hub = Hub()
# since we are running outside asyncio, we need a main_loop
main_loop = asyncio.get_event_loop()
# discover new tags
main_loop.run_until_complete(hub.discover_tags())
print(hub.tags)
if len(hub.tags) < 0:
    print("sorry - no tags discovered")
    os.Exit(0)
# select the first discovered tag - you should rather use hub.getTagByName("your-address")
tag = hub.tags[0]
# get the tags config - important to be able to decode the messages from the tag
main_loop.run_until_complete(tag.get_config())
print(tag.config.get_props())
# get the log
main_loop.run_until_complete(tag.get_acceleration_log())
# generate a json string
# output file
tagjs = json.dumps(hub, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4)
file = open("./acceleration_log.json", "w")
file.write(tagjs)
file.close()