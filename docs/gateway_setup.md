# Gateway
## Cloning gateway repository
### Create SSH key
To clone the Gateway [repository](https://github.com/bchwtz-fhswf/gateway) onto your Pi, you again need to create a SSH Key and connect it to your account ([compare see here](./sensor_setup.md#Software Setup)). Generate it by following the instructions [here](https://docs.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent for Linux) (you dont have to pass it to a key agent) and add it to your account by following [these instructions](https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account):
```{bash, eval=F}
ssh-keygen -t ed25519 -C "your_email@example.com"
```
  
## Checking out the repository
Now let's checkout the current state of this repository and change into its folder
```{bash}
git clone https://github.com/bchwtz/bchwtz-gateway.git gateway && cd gateway
```
## Setting up local python environment
In this step you have to set up a local python environment. See [here](./useful_tips.md).

## Install python packages
Install the following python packages into your environment:
```{bash, eval=F}
source /path/to/your/env/bin/activate

pip3 install ruuvitag_sensor
pip3 install crcmod
pip3 install pygatt
pip3 install interruptingcow
pip3 install -r requirements.txt
sudo apt-get install bluez bluez-hcidump
```

## Setting up shell scripts
Run the following command in the "gateway" folder to install the gateway and configure the environment variables:
```{bash}
./install_gw.sh
```

If you also want to set up the MkDocs tools to edit the documentation (optional) just run:
```{bash}
./install-docs-req.sh
```

## Add gateway folder to $PATH
In order to make it easier to run scripts that reference the gateway package, the folder where it is located needs to be added to the python path variable. This problem can be solved in the following way:

1. Open the _activate_ file for your virtual env:
```{bash}
nano /path/to/venv/bin/activate
```
Here insert the following line at the end, where the path references the cloned repository folder.
```{bash}
export GATEWAY_PATH="abs/path/to/your/cloned/gateway-folder"
```
Once done, save and exit. Reload the environment with
```{bash}
deactivate
source /path/to/venv/folder/bin/activate
```
Now you should be able to get the value of the new env variable by running
```{bash}
echo $GATEWAY_PATH
```
If you want your python scripts to be able to reference the gateway package from everywhere, you just need to add the following lines to
their imports:
```{python}
import os
import sys

sys.path.append(os.environ["GATEWAY_PATH"])
```
## Setting up services locally
To setup the mircoservices locally you need to have docker installed, if you do not have docker on your system, please run:
```{bash}
sudo apt update && sudo apt install docker.io docker-compose
sudo usermod -aG docker pi
```
This will download and install the necessary packages as well as put your user ("pi" in this case, change if needed) into the correct user group.
## Running the infrastructure
Spin up the necessary docker-compose file that starts the MongoDB server etc.
```{bash}
# in gateway folder
./run_on_pi.sh
```
or 
```{bash}
# in gateway/deployments/gateway
docker-compose up -d
cd -
```
## Running the gateway-service
Running the gateway service itself which serves as a hub for the tags.

```{bash}
python3 gateway.py
```
More information on when to run it can be found [here](./useful_tips.md).

## Installing go
In order to use the CLI you need to install golang. This can be done by running
```{bash}
sudo apt install golang
```
## Running the database service
To run the automated database dumper service:
```{bash}
# in gateway/storage-and-control
go run cmd/db_dumper/main.go
```

## Running the CLI
Running CLI which allows to access certain functionalities of the tag.([see here](./go_cli.md))
```{bash}
# from everywhere
gw tags get
```
or
```{bash}
# in gateway/storage-and-control
go run cmd/cli/main.go tags get
```

## Docker problems
Check out if docker containers are running via
```{bash}
docker ps
```
All containers should be up apart from "gateway_ble-gateway_1" which constantly restarts. If the "gateway_mongo_1" container is not running correctly you need to change the following settings in "docker-compose.rpi.yml" in the "gateway/deployments/gateway" folder:  

1. services:  
	ble-gateway:  
	environment:  
	MQTT-broker: mqtt-broker
	
2. services:  
	db-dumper:  
	environment:  
	MQTT-broker: mqtt-broker  
	
Additionally you need to change the following entry in "docker-compose.yml" in the same folder in order to downgrade the mongodb version:  

3. mongo:  
	image: mongo:4.4.18

and then run the following commands to redownload the mongodb image and restart the docker containers. 
```{bash}
# in gateway/deployments/gateway
docker-compose -f docker-compose.rpi.yml -f docker-compose.yml --env-file ../../.env down
docker-compose -f docker-compose.rpi.yml -f docker-compose.yml --env-file ../../.env up -d
```

Congratulations! You're all set!
READ THE [DEVELOPMENT PRINCIPLES](global_architecture/development_principles.md) FOR THIS PROJECT - ALL COMMITS NOT COMPLYING WILL BE DELETED IMMEDIATLY!
