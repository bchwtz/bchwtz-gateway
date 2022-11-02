from time import sleep

import asyncio
import uuid
from gateway.config import Config
from gateway.hub.hub import Hub
# Config.load_from_environ()

hub = Hub()
print("spawned gw")
main_loop = asyncio.get_event_loop()
# main_loop.run_until_complete(gw.hub.discover_tags())

# main_loop.run_until_complete(gw.hub.tags[0].get_config())
# for tag in gw.hub.tags:
#     print(tag.name)
#     main_loop.run_until_complete(tag.get_time())
# sleep(20)
# print(gw.hub.tags[0].time)
main_loop.run_until_complete(hub.discover_tags())
print(hub.tags)
tag = hub.tags[0]


main_loop.run_until_complete(tag.get_config())
print(tag.config.get_props())
# tag.config.scale = 2
# main_loop.run_until_complete(tag.set_config())
main_loop.run_until_complete(tag.get_acceleration_log())
