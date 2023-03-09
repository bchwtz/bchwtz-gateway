import sys
import json
import pandas as pd

filename = sys.argv[1]

with open(filename) as f:
    data = json.load(f)[0]

    #tag_address = data[0]["tag"]["address"]
    #tag_name = data[0]["tag"]["name"]
    #tag_time = data[0]["tag"]["time"]

    measurement_list = []

    for measurement in data[1:]:
        if "measurement" in measurement:
            if isinstance(measurement["measurement"], dict):
                measurement_list.append(measurement["measurement"])
            else:
                for m in measurement["measurement"]:
                    measurement_list.append(m)

    df = pd.DataFrame(measurement_list)

    df = df.drop(["gathering_type", "measurements", "sequence_number"], axis=1)
    cols = df.drop("recorded_time", axis=1).columns.to_list()

   # df["tag_address"] = tag_address
   # df["tag_name"] = tag_name

    df["timestamp"] = pd.to_datetime(df.recorded_time, unit="ms")

    #df = df[["tag_address", "tag_name", "timestamp", "recorded_time"] + cols]
    df = df[["timestamp", "recorded_time"] + cols]


    df = df.sort_values(by=["timestamp"])

    df = df.set_index("timestamp")

    df.to_csv("convert.csv")

    print("Created csv export!")
