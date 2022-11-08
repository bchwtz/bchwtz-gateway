# User setup

## Getting started

If you just want to run a gateway on a raspberry pi, you are just right here! First of all you should check all prerequisites and then choose your setup method. This manual will use raspbian on a raspberry pi 4. But any raspberry pi or debian system should work the same.

## Prerequesites
To run the software you will need:

* a debian-based linux (or arch)
* a raspberry pi 4
* docker
* git

## Install requirements

In any case you should install git and docker on your platform:
```{bash}
sudo apt update
sudo apt install git docker.io
# adding pi to docker group now, so we can use docker without root
sudo usermod -aG docker pi
```
After this step you have to logout and login.

## Cloning the repository
```{bash}
git clone https://github.com/bchwtz/bchwtz-gateway.git gateway && cd gateway
```

## Running the software in docker (recommended)
This step will run all required components inside a docker container.

```{bash}
./run_on_pi.sh
```

## Download the go client
To be able to run the go client on a raspberry pi please head to the [releases page](https://github.com/bchwtz/bchwtz-gateway/releases) and download the gw_arm64 bin to your projects folder on the pi.  
The following should work then:
```{bash}
mkdir -p bin
# moves the binary of the cli to a new folder named bin
mv gw-arm64 bin/gw
# changes the execution rights
chmod +x bin/gw
```

You're all set!