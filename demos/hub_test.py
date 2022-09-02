import asyncio
import time
from gatewayn.hub.hub import Hub

hub = Hub()
main_loop = asyncio.get_event_loop()
main_loop.run_until_complete(hub.listen_for_advertisements())

# testtag = hub.get_tag_by_name("Ruuvi 048B")
# testtag.get_time()
# testtag.get_config()
# testtag.config.set_samplerate(1)
# testtag.config.set_scale(4)
# testtag.config.set_divider(1)
# testtag.set_config()
# testtag.get_config()
# print(testtag.__dict__)
# print(testtag.config.__dict__)
# print(testtag.time)
# testtag.set_time_to_now()