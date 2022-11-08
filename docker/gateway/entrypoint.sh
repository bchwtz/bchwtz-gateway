#!/bin/bash

service dbus start
bluetoothd &

env > .env && python demos/demo_gateway.py