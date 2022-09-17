# Docker Composition

Configure environment variables and run Mainflux Docker Composition.

*Note**: `docker-compose` uses `.env` file to set all environment variables. Ensure that you run the command from the same location as .env file.

## Installation

Follow the [official documentation](https://docs.docker.com/compose/install/).


## Usage

Run following commands from the deployments directory.

```
docker-compose -f docker/docker-compose.yml up
```

## Github Actions Pipeline

Usually the Github Actions Pipeline (can be found in .gihtub/workflows) will manage deployment and execution of the mainflux-cluster. It may be triggered using the github UI or by commiting to the main or mf-deployment branches.