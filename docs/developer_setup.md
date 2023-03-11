# Developer setup

## Checking out the repository
First, let's checkout the current state of this repository:

```{bash}
git clone https://github.com/bchwtz/bchwtz-gateway.git gateway && cd gateway
```

## Setting up services locally
To setup the mircoservices locally you need to have docker installed, if you do not have docker on your system, please run:

```{bash}
sudo apt update && sudo apt install docker.io docker-compose
sudo usermod -aG docker pi
```

## Running the infrastructure
Spin up the necessary docker-compose file:

```{bash}
cd deployments/gateway
docker-compose up -d
cd -
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

## Running the database service

```{bash}
cd storage-and-control
go run cmd/db_dumper/main.go
```

## Running the cli

```{bash}
cd storage-and-control
go run cmd/cli/main.go tags get
```

Congratulations! You're all set!
READ THE [DEVELOPMENT PRINCIPLES](../global_architecture/development_principles) FOR THIS PROJECT - ALL COMMITS NOT COMPLYING WILL BE DELETED IMMEDIATLY!