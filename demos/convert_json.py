"""
This demo script reads in the output JSON file of the acceleration log (via CLI), stores it as a dataframe and uses peakfinding (plus draws a plot)
"""
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt 
from scipy.signal import find_peaks
import argparse

def find_and_plot_peaks(df,startrange,endrange,plotpath,column="acc_z"):
    """
    Peakfinding is done with the help of the python package 'scipy' which has a wide range of signal processing tools. As
    a simple example the peak finding module (find_peaks()) is used to determine peaks in our data. Startrange and endrange can be used
    to set the region of the signal in which you want to look for peaks.
    """
    x = df[column]
    x_start = x[0:startrange]
    x_end = x[endrange:-1]
    
    peaks, _ = find_peaks(x_start, prominence=1)      
    peaks_end, _ = find_peaks(x_end, prominence=1)

    peaks_end += endrange

    peaks = np.concatenate((np.array(peaks), np.array(peaks_end)), axis=0)

    plt.plot(peaks, x[peaks], "xr"); plt.plot(x); plt.legend(['prominence'])
    plt.savefig(plotpath)
    plt.show()

    print(peaks)

def main():
    """
    In the main function the arguments are parsed, then the JSON file containing the dataset is loaded and list
    comprehension is used to filter out data before loading it as a dataframe.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-jp","--json_path", help="path to acceleration log in JSON format")
    parser.add_argument("-pp","--plot_path", help="save location for peak-plot", default="peak_plot.png")
    parser.add_argument("-sr","--start_range", help="percentage of sample-range that is considered for starting points", default=0.3)
    parser.add_argument("-er","--end_range", help="percentage of sample-range that is considered for ending points", default=0.3)
    args = parser.parse_args()

    if args.json_path == None:
        print("Argument '--json_path' required. exiting...")
        exit()

    # print(args.json_path)
    # print(args.plot_path)
    # print(args.start_range)
    # print(args.end_range)

    with open(args.json_path) as file:
        data = json.load(file)

    # create dataframe
    ds = [d["measurement"] for i,d in enumerate(data[0]) if i != 0 and d["measurement"]["gathering_type"] == "logging_data"]
    df = pd.DataFrame(ds)

    start_range = int(len(df)*float(args.start_range))
    end_range = int(len(df)*(1-float(args.end_range)))

    find_and_plot_peaks(df,start_range,end_range,args.plot_path)

if __name__ == "__main__": 
    main()