## Usefull Informations for Preperation

There are some tricks to communicate with RaspberryPi and get Python Code run. The aim of this chapter is to give a brief 
introduction to the installation and application of the packages.

## Installation

Before installing, a few [settings](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token) 
have to be made, so that the gateway gets access to the private repository.

    1. Go to Github>Settings>Developer Settings>Personal Access tokens
    2. Creat a new access token for the RaspberryPi
    3. To acces to the repository via comand line, select `repo`
    4. Copy the token

```{admonition} Note
The token is displayed by github only once for copy in plain text.
If the token is lost, the process must be repeated.
```

The software can be installed via command line.

```{code-block} python
pip3 install -e git+https://<access token>@github.com/bchwtz-fhswf/gateway.git@develop#egg=gateway
```

```{admonition} Note
We used to push the latest changes into the develop branche. If you want to install a specific version,
the last comand segment has to be changed (e.g. ...@main#egg=gateway).
```

Performing the installation requires ’sudo' permissions. When executing the command line, 
a corresponding login with the necessary rights is required. Dependent libraries and packages 
are now installed. Feedback will be returned if the installation is successful.

```{code-block} python
Defaulting to user installation because normal site-packages is not writeable
Looking in indexes: https://pypi.org/simple, https://www.piwheels.org/simple
Obtaining gateway from git+https://github.com/bchwtz-fhswf/gateway.git@develop#egg=gateway
  Updating ./src/gateway clone (to revision develop)
  Running command git fetch -q --tags
Username for 'https://github.com': <username>
Password for 'https://<username>@github.com':
  Running command git reset --hard -q 38b0e0af30a41759ebcfd8be822870358268d75b
Requirement already satisfied: asyncio in ./.local/lib/python3.7/site-packages (from gateway) (3.4.3)
Requirement already satisfied: nest_asyncio in /usr/local/lib/python3.7/dist-packages (from gateway) (1.5.1)
Requirement already satisfied: regex in ./.local/lib/python3.7/site-packages (from gateway) (2021.8.3)
Requirement already satisfied: bleak in ./.local/lib/python3.7/site-packages (from gateway) (0.11.0)
Requirement already satisfied: crcmod in ./.local/lib/python3.7/site-packages (from gateway) (1.7)
Requirement already satisfied: async_timeout in ./.local/lib/python3.7/site-packages (from gateway) (3.0.1)
Requirement already satisfied: configparser in ./.local/lib/python3.7/site-packages (from gateway) (5.0.2)
Requirement already satisfied: dbus-next in ./.local/lib/python3.7/site-packages (from bleak->gateway) (0.2.2)
Installing collected packages: gateway
  Attempting uninstall: gateway
    Found existing installation: gateway 1.2.0
    Uninstalling gateway-1.2.0:
      Successfully uninstalled gateway-1.2.0
  Running setup.py develop for gateway
Successfully installed gateway
```

```{admonition} Note
The Setup.py can also be run offline. To do this, the code line `sudo python Setup.py install` 
must be executed from the project directory.
```

## Get Sensor Data

The file ’SensorGatewayBleak.py' can now be imported as a library in any PythonIDE. 
The functions of the library can be tested with the following code lines.

```{code-block} python
Ruuvi_Com_Obj = SensorGatewayBleak.RuuviTagAccelerometerCommunicationBleak() 

Ruuvi_Com_Obj.deactivate_logging_at_sensor()
Ruuvi_Com_Obj.activate_logging_at_sensor()
Test = Ruuvi_Com_Obj.get_acceleration_data()
```

The logging of the Accelorometer data is reseted by the disabling/activating function. 
The data will be returned as a list.
