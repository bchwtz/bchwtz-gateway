"""
This demo shows how to get and print the current config of your tag via python as well as editing it.
This is done by reading the option values from a config file, parsing these and then use functions from the gateway
package to set the new values. It's important to note that the values for each individual option have to be set before
calling "tag.set_config()" as the latter writes the settings to the tag device.
"""
import os
import sys
"""
Read system environment variables and insert path to gateway folder to be able to run this script from every folder
"""
# absolute: might need to change folders
# sys.path.append("/home/testuser/gateway")
# absolute from env variable
sys.path.append(os.environ["GATEWAY_PATH"])
# relative
# sys.path.append("../../../gateway")

import asyncio
import json
import sys
import configparser
import argparse

# from gateway.config import Config
from gateway.hub.hub import Hub
# from hub.hub import Hub

def set_values(tag,sr,scale,res,div,dsp_func,dsp_param,mode):
    """
    Setting values for the individual options.
    """
    tag.config.set_samplerate(sr)
    tag.config.set_scale(scale)
    tag.config.set_resolution(res)
    tag.config.set_divider(div)
    tag.config.set_dsp_function(dsp_func)
    tag.config.set_dsp_parameter(dsp_param)
    tag.config.set_mode(mode)
    return tag

def main():
    """
    Parsing of arguments (config file path), creation of main async loop, discovery of tag(s), waiting for current config values (for reference)
    and then setting of new values by calling the function "set_values()". Afterwards these settings get written to the tag via "tag.set_config()".
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-cp","--config_path", help="path to config file for tag", default="config.cfg")
    args = parser.parse_args()

    cfg_file = args.config_path

    config = configparser.ConfigParser()
    config.read(cfg_file)

    samplerate = int(config.get("Tag", "samplerate"))
    scale = int(config.get("Tag","scale"))
    resolution = int(config.get("Tag","resolution"))
    divider = int(config.get("Tag","divider"))
    dsp_function = int(config.get("Tag","dsp_function"))
    dsp_parameter = int(config.get("Tag","dsp_parameter"))
    mode = str(config.get("Tag","mode"))
    tag_address = str(config.get("Tag","address"))

    hub = Hub()
    main_loop = asyncio.get_event_loop()
    main_loop.run_until_complete(hub.discover_tags())

    if len(hub.tags) < 1:
        print("sorry - no tags discovered -> exiting")
        sys.exit(0)

    tag = hub.get_tag_by_address(tag_address)

    main_loop.run_until_complete(tag.get_config())

    print(f"tag.config before: {tag.config.get_props()}")

    tag = set_values(tag,samplerate,scale,resolution,divider,dsp_function,dsp_parameter,mode)
    
    main_loop.run_until_complete(tag.set_config())
    main_loop.run_until_complete(tag.get_config())

    print(f"tag.config after: {tag.config.get_props()}")

if __name__ == "__main__":
    main()
