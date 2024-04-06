This shell script uses the CLI interface to get the acceleration log of a specific tag (as JSON), then calls the [_convert_json.py_](./demo_convert_peak.md) script to convert the log to a dataframe and find peaks. Afterwards the contents of the log are written to a mongo db database by calling [_insert_into_mongodb.py_](./demo_mongodb_ref.md). The latter expects the mongodb password (stored in environment variable _$MONGO_PASSWORD_) as well as the path to the JSON output of the acceleration log.
```{bash}
#!/bin/bash

DEVICE_ID=F0:CB:45:2B:51:0B
ACCFILE="walking_hand_5_10.json"
OUTPUT_PLOT_PATH="peak_plot.png"
START_RANGE=0.2
END_RANGE=0.2

gw tags get acceleration_log --address $DEVICE_ID --file $ACCFILE
python convert_json.py --json_path $ACCFILE --plot_path $OUTPUT_PLOT_PATH --start_range $START_RANGE --end_range $END_RANGE
python insert_into_mongodb.py -p $MONGO_PASSWORD --json_path $ACCFILE
```
** Important Comment **  
This script (like all python scripts that try to access the ruuvi tags) should be run without an active instance of "gateway.py" running.
