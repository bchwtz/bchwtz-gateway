#!/bin/bash

DEVICE_ID=F0:CB:45:2B:51:0B
ACCFILE="walking_hand_5_10.json"
OUTPUT_PLOT_PATH="peak_plot.png"
START_RANGE=0.2
END_RANGE=0.2

gw tags get acceleration_log --address $DEVICE_ID --file $ACCFILE
python convert_json.py --json_path $ACCFILE --plot_path $OUTPUT_PLOT_PATH --start_range $START_RANGE --end_range $END_RANGE
python insert_into_mongodb.py -p $MONGO_PASSWORD --json_path $ACCFILE
