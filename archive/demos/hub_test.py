import asyncio
import asyncbg
import time
import json
from gateway.api.api import API
from gateway.hub.hub import Hub

hub = Hub()
main_loop = asyncio.get_event_loop()
async def print_tags(hub: Hub):
        while True:
            await hub.listen_for_advertisements(5)
            dtags = []
            for tag in hub.tags:
                for sensor in tag.sensors:
                    print(sensor.__dict__)
            #     dtags = tag.__dict__
            #     dtags["new_sensors"] = []
            #     for sensor in tag.sensors:
            #         dtags["new_sensors"].append(sensor.__dict__)
            #     print(tag.__dict__)
            # with open("data/tags.json", "w") as f:
            #     del dtags["ble_device"]
            #     del dtags["ble_conn"]
            #     del dtags["logger"]
            #     del dtags["sensors"]
            #     del dtags["enc"]
            #     del dtags["dec"]
            #     del dtags["config"].logger
            #     json.dump(dtags, f)
            # time.sleep(10)

main_loop.run_until_complete(print_tags(hub))
# api = API()
# api.setup_routes()
# asyncio.run(api.run())

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