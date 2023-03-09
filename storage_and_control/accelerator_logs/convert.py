import json
import pandas as pd

with open("test.json") as f:
    data = json.load(f)[0]

    tag_address = data[0]["tag"]["address"]
    tag_name = data[0]["tag"]["name"]
    tag_time = data[0]["tag"]["time"]

    measurement_list = []

    for measurement in data[1:]:
        if "measurement" in measurement:
            for m in measurement["measurement"]:
                measurement_list.append(m)

    #measurement_list = [m for m in measurement["measurement"] for measurement in data[1:] if "measurement" in measurement]
    print(type(measurement_list[0]))

    df = pd.DataFrame(measurement_list)
    df.to_csv("convert.csv")


    print(len(data))
    print(tag_address)
    print(tag_name)