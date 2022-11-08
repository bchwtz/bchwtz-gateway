# Docker, deployments and github actions
The project heavily relies on docker and docker-compose to run the microservices.

## Directory structure

* **deployments/gateway:** has all docker-compose deployments refering to this project
* **docker/gateway:** has the Dockerfile you need to build a new version of the ble_gateway image
* **storage_and_control/docker/dumper:** has the Dockerfile of the db_dumper
* **.github/workflows:** has the github action workflows which will automatically build all docker-images and the documentation on every push or merge on main

## Github action workflows

* **ble-gateway:** This workflow builds a docker-image of the ble_gateway
* **cleanup:** Deletes nightly artifacts that are older than 1 day
* **mkdocs_wf:** Builds and publishes the documentation
* **storage_and_control:** Builds the go-binaries and packages a docker-image for the db_dumper service. This will be done for linux/arm64 and linux/amd64