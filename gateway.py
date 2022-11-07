from time import sleep
from gateway.gateway import Gateway
import asyncio
from gateway.config import Config
import argparse

def main():
    # Config.load_from_environ()
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--discovery", help="Classic discovery mode", action="store_true")

    gw = Gateway()
    print("spawned gw")
    main_loop = asyncio.get_event_loop()

    args = parser.parse_args()
    if args.discovery:
        print("running in discovery mode")
        main_loop.run_until_complete(gw.run_discovery())
    else:
        print("running in advertisement mode")
        main_loop.run_until_complete(gw.get_advertisements())

if __name__ == "__main__" :
    main()