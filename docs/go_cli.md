# How to use the gateway-cli

## Basic command structure of the client
The commandline interface (cli) is structured as expressive cli.
```{ bash }
gw <command> <subcommand> <subcommand>... --<flag> <named_argument> <argument>
```
Example:  
The following prompt will get all tags and their measurements that are known by the gateway and dump them as a json to the given file.
```{bash}
gw tags get --file test.json
```
This will do the same thing but only with one tag (in this case ff:ff:ff:ff:ff:ff):
```{bash}
gw tags get --address ff:ff:ff:ff:ff:ff --file test.json
```
## Help - I'm stuck!
just type "help" at any point
```{bash}
gw tags get --help
```
# Exposed functions
## get
Get will always instruct the gateway to fetch data from one or more tags. It will not always return data directly, usually the `gw tags get` prompt is used to fetch data.
### tags
This command fetches tag information from the gateway and returns them into go structs. If --file is given, the data will be output as a json into the given file.
```{bash}
gw tags get --address ff:ff:ff:ff:ff:ff --file test.json
```

### config
Gets the config from one or more tags. Will only report if it was fetched successfully.
```{bash}
gw tags get config --address ff:ff:ff:ff:ff:ff
```

### time
Gets the time from one or more tags. Will only report if it was fetched successfully.
```{bash}
gw tags get time --address ff:ff:ff:ff:ff:ff
```

### acceleration_log
Will fetch an acceleration log from one or more tags. As soon as the first tag returns its values, it is going to dump all measurements to the given --file filename as json.
```{bash}
gw tags get acceleration_log --address ff:ff:ff:ff:ff:ff --file test.json
```

## set
Sets parameters on one or more tags - depends on --address
### config
Validates and sets the given config to one or more tags. If values are not valid, the old value will be set again. --config has to be a valid json.
```{bash}
gw tags set config --address ff:ff:ff:ff:ff:ff --config '{""}'
```

### time
Sets the current time on one or more tags - depends on --address
```{bash}
gw tags set time --address ff:ff:ff:ff:ff:ff
```

### heartbeat
Sets the heartbeat on one or more tags - depends on --address. --heartbeat is mandatory!
```{bash}
gw tags set heartbeat --address ff:ff:ff:ff:ff:ff --heartbeat 10
```

## stop
Commands that are able to stop processes on a tag. Until now you can only stop acceleration logging
```{bash}
gw tags stop acceleration_log --address ff:ff:ff:ff:ff:ff
```