# How to use the gateway-cli

## Command structure of the client
The commandline interface (cli) is structured as expressive cli.
```{bash}
gw <command> <subcommand> <subcommand>... --<flag> <argument>
```
Example:
This will get all tags that are known by the gateway and dump them as a json to the given file.
```{bash}
gw tags get --file test.json
```
This will do the same thing but only with one tag:
```{bash}
gw tags get ff:ff:ff:ff:ff:ff --file test.json
```

## How to use the help of the cli
just type "help" at any point
```{bash}
gw tags get --help
```