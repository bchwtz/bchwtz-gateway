from gatewayn.gateway import Gateway
import asyncio
from gatewayn.config import Config

# Config.load_from_environ()

gw = Gateway()
print("spawned gw")
asyncio.get_event_loop().run_until_complete(gw.run())