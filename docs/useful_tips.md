# Useful tips
## Python environment
### Create python environment
You can set up a local python environment by running the following commands.
```{bash, eval=F}
python3 -m venv_name /path/to/venv/folder
```
  
### Activating local python environment
You can activate a local python environment for the current terminal session by running the command below:
```{bash}
source /path/to/venv/folder/bin/activate
```

### Installing packages to local python environment
Packages can be install via pip. If you have already activated (see previous step) the environment, you can just run
```{bash}
pip install package_name
```
If you don't want to activate the environment yet still want to install a package via pip you can do it by using the following command:
```{bash}
/path/to/venv/folder/bin/pip install package_name
```

## Gateway service (gateway.py)
If you want to utilize the CLI via "gw" commands from the terminal, you need to have "gateway.py" running in order to access the tags and open connections.  
To connect via python you have to shut down "gateway.py" first.
```{bash}
sudo apt update && sudo apt install docker.io docker-compose
sudo usermod -aG docker pi
```

## Enable SSH for VSCode
VSCode offers the extension "Remote-SSH" which allows you to connect and use VSCode remotely to edit the files on your Raspberry Pi. This is very useful and can easily be activated by simply installing the extension and using the new button on the bottom left of VSCode to connect to your remote device via
```
ssh username@RASPI-IP
```
More information can be found [here](https://code.visualstudio.com/docs/remote/ssh-tutorial).
## MongoDB
### Accessing MongoDB docker container
You can access the MongoDB docker container by running the following command:
```{bash}
docker exec -it gateway_mongo_1 bash
```
This will open a terminal in the docker container which allows you to get the correct login information for the MongoDB session (needed for python scripts, compare [here](./demo_mongodb_ref.md)).
```{bash}
echo $MONGO_INITDB_ROOT_PASSWORD
```
You can then connect to the mongo shell in the docker container via
```{bash}
mongo -u mongo -p $MONGO_INITDB_ROOT_PASSWORD
```
In this mongo shell you can utilize different mongo commands, for example:
```
# show databases
show dbs

# select database "gateway"
use gateway

# create collection "accel_meas"
db.createCollection("accel_meas")

show collections

db.accel_meas.find()
db.accel_meas.findOne()
```

### Manually storing MongoDB login password as environment variable
The MongoDB password should be set in the _$MONGO_PASSWORD_ variable. If this is not the case you can get the password by doing the following steps.  
As the login password is stored as environment variable in the docker container itself, we need to add it to the environment variables of the virtual environment on the Raspberry Pi in order to make it easier to use in scripts etc.  
This can be easily done by getting the password via the method described above. Afterwards run the following command to open .bashrc for writing:
```
nano /path/to/python/venv/bin/activate
```
Add the following line to the end of this file:
```
export MONGO_PASSWORD="the_password"
```
Now this variable will be available as environment variable after reloading the file with:
```
source /path/to/python/venv/bin/activate
```  
    
READ THE [DEVELOPMENT PRINCIPLES](global_architecture/development_principles.md) FOR THIS PROJECT - ALL COMMITS NOT COMPLYING WILL BE DELETED IMMEDIATLY!
