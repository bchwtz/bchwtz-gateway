import asyncio
import time
from gateway.api.api import API
from gateway.hub.hub import Hub

hub = Hub()
main_loop = asyncio.get_event_loop()

# main_loop.run_until_complete(hub.listen_for_advertisements(0))

api = API()
api.setup_routes()
asyncio.run(api.run())