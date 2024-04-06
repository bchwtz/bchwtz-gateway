# Current bugs
Due to current ongoing developments the information on this page could be outdated at the beginning of the next iteration of this course. 
## Firmware version
Depending on the firmware version used the accelerometer might not work as intended, or rather it will not correctly store the output and never report back. If the following command does not return a JSON file with 1000s of samples you might need to update/get another version of the firmware:
```{bash}
gw tags get acceleration_log --address [address] --file [filename]
```
Always check if _gateway.py_ is running as this is needed for any of the CLI commands to work as it manages the connections.

## Get acceleration log
Calling the ruuviTag acceleration measurement via the CLI

```{bash}
gw tags get acceleration_log --address [address] --file [filename]
```
will lead to sampling on the tag, but the recorded data does not resemble the engaged activity (when compared to measurement data from other accelerometers) and in general does not seem to pick up much information, independent of settings like sampling rate etc.  
After running this command once it does not work again most of the time for various reasons: 

1. Memory full, does not get cleared and same data gets returned again. Can be fixed by stopping the gateway python script and restarting the tag by takng out the memory. Restart the gateway and insert the battery back in, then it should usually work.

2. Tag gets stuck during logging mode and is unable to perform any other operations afterwards. Fix by restarting tag and gateway.
There are probably other reasons as well why this does not work correctly, but these were the ones that stuck out.


## Database dumper
The db dumper does currently not work as intended as it does not write any data to the MongoDB.
