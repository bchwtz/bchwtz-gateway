# Developer setup

## Checking out the repository
First, let's checkout the current state of this repository:

```{bash}
git clone https://github.com/bchwtz/bchwtz-gateway.git && cd gateway
```

## Setting up services locally
To setup the mircoservices locally you need to have docker installed, if you do not have docker on your system, please run:

```{bash}
sudo apt update && sudo apt install docker.io docker-compose
```

## Installing the python packages
```{bash}
pip3 install -r requirements.txt
```

## Running the gateway-service
Running the gateway service itself:

```{bash}
python3 gateway.py
```

Congratulations! You're all set!