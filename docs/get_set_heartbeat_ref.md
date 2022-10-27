__Getting the Heartbeat__
::: demos.get_heartbeat_demo


__Setting the Heatbeart__
::: demos.set_heartbeat_demo

Currently both of the demos are configurated to run their respective action ten (10) times.
This is so you can create logging files, which then can be used by the analyse_heartbeats.py-script.
To do so, you need to run the scripts as follows:
```{bash}
python3 demos/get_heartbeat.py > path_to_logging_file.txt
```