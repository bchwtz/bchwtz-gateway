## Getting-Started with gateway-Preperation

Before you start to run the first codelines follow the steps below:
  1. Make sure your RaspberryOS is up to date
    - `sudo apt-get update` + `sudo apt-get upgrade`
  2. Install BlueZ in order to use the advertisement functions of the gatway
    - `sudo apt-get install bluez bluez-hcidump`
  3. Follow the instructions of the `docs\git_installation_on_raspberrypy.md`

## Installation

To install the project on your RaspberryPi switch to the direcory where the git-clone lays.

`cd /path/to/gatewy-main`

Install this project as python package.

`python3 setup.py install`

If the installation was successful, the following output should be seen:

```{code-block} bash
Using /usr/lib/python3/dist-packages
Searching for Jinja2==2.11.3
Best match: Jinja2 2.11.3
Adding Jinja2 2.11.3 to easy-install.pth file

Using /usr/lib/python3/dist-packages
Searching for pyparsing==3.0.6
Best match: pyparsing 3.0.6
Processing pyparsing-3.0.6-py3.9.egg
pyparsing 3.0.6 is already the active version in easy-install.pth

Using /usr/local/lib/python3.9/dist-packages/pyparsing-3.0.6-py3.9.egg
Searching for pytz==2021.3
Best match: pytz 2021.3
Processing pytz-2021.3-py3.9.egg
pytz 2021.3 is already the active version in easy-install.pth

Using /usr/local/lib/python3.9/dist-packages/pytz-2021.3-py3.9.egg
Finished processing dependencies for gateway==1.2.0
```

The software can be installed via command line.

```{code-block} python
pip3 install -e git+https://<access token>@github.com/bchwtz-fhswf/gateway.git@develop#egg=gateway
```
```{admonition} Note
The token is displayed by github only once for copy in plain text.
If the token is lost, the process must be repeated.
```

## Get Sensor Data

The gateway library consists of three main modules (`sensor_hub`, `sensor` and `experimental`).
Primary tasks of the sensorhub are:
 - Find `Tags`
 - Create digital twins
 - listen to advertisements

```{code-block} python
from gateway import sensor_hub
myHub = sensor_hub.sensor_hub()
myHub.discover_neighborhood()
# If a Tag was found, the sensor_hub generates an object sensor and stores it in myHub.sensorlist
#print(myHub.sensorlist[0], type(myHub.sensorlist[0])
sensor1 = myHub.sensorlist[0]
sensor1.get_sensor_time()
```

