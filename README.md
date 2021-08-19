# Getting-Started Guide

## Installation

Die Läuffihigkeit der Software kann lediglich unter Raspbian mit einem entsprechenden 
RaspberryPi als Hardware garantiert werden. Die Software wird via Kommandozeile 
installiert.

```{code-block} python
pip install -e git+https://github.com/bchwtz-fhswf/gateway.git@develop#egg=gateway
```

Die Durchführung der Installation erfordert `sudo` Berechtigungen. Bei Ausführung der
Kommandozeile wird ein entsprechender Login mit den notwendigen Rechten gefordert.
Bei erfolgreicher Ausführung werden nun abhängige Bibliotheken installiert und abschließend 
das Hauptprogramm installiert.

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

```{admonition} Hinweis
Die `Setup.py` kann auch offline ausgeführt werden. Dazu muss aus dem Projektverzeichnis aus die 
Codezeile `sudo python Setup.py install` ausgeführt werden.
```

## Get Sersor Data

Die Datei `SensorGatewayBleak.py` kann nun als Bibliothek in einer beliebigen PythonIDE
importiert werden. Die Funktionen der Bibliothek können mit den nachfolgenden Codezeilen
einzeln getestet werden.

```{code-block} python
Ruuvi_Com_Obj = SensorGatewayBleak.RuuviTagAccelerometerCommunicationBleak() 

Ruuvi_Com_Obj.deactivate_logging_at_sensor()
Ruuvi_Com_Obj.activate_logging_at_sensor()
Test = Ruuvi_Com_Obj.get_acceleration_date()
```

Das Logging der Accelorometerdaten wird reseted durch das deaktivieren/aktivieren.
Die Daten werden als Liste zurückgegeben.