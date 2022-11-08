#!/bin/bash

service dbus start
bluetoothd &

env > .env && python gateway.py