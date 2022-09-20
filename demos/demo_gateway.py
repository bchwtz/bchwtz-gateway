from time import sleep
from gatewayn.gateway import Gateway
import asyncio
from gatewayn.config import Config

# Config.load_from_environ()

gw = Gateway()
print("spawned gw")
main_loop = asyncio.get_event_loop()
main_loop.run_until_complete(gw.hub.discover_tags())

# main_loop.run_until_complete(gw.hub.tags[0].get_config())
for tag in gw.hub.tags:
    print(tag.name)
    main_loop.run_until_complete(tag.get_time())
sleep(20)
print(gw.hub.tags[0].time)
# main_loop.run_until_complete(gw.get_advertisements())