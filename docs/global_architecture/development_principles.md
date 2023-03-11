# Development principles
As we are using microservices, each new function that is not directly connected to bluetooth functionality, such as databases, clients, gateways, and others shall be implemented in their own repositories/subdirectories of this project.  
NEVER add code of other languages to one part of the project - for example go-code to parts of the project which are written in python or vice versa!

## Directory structure

* **deployments:** has all docker-compose deployments refering to this project
* **docker:** has the Dockerfile you need to build a new version of the corresponding image
* **storage_and_control:** sample implementation of a db_dumper and a client written in go - you are free to implement your own client in whatever language you might choose. Just attach yourself to the MQTT broker
* **.github/workflows:** has the github action workflows which will automatically build all docker-images and the documentation on every push or merge on main