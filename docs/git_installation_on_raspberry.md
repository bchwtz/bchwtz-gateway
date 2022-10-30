# How to setup Git on a Raspberry Pi

## Installing Git with Apt
The Git package is included in the OS defaults of any Raspberry, therefore you can run the following code as admin user, called "root" on the Raspberry.
``` bash
sudo apt update
```
to make sure you have the newest version and then type
``` bash
sudo apt install git
```
Enter the command below to check whether the installation was succesful:
``` bash
git --version
```
Output at time of writing this documentation:
``` bash
git version 2.30.2
```
That’s it! You have installed Git on your Raspberry Pi.

## First steps in using Git on Raspberry

First, you need to clone the repository to your Raspberry. You do this with the following code:
``` bash
git clone git@github.com:bchwtz-fhswf/gateway.git
```
Now, switch to the correct path, where the repository was copied to.
``` bash
cd gateway
```
Checkout a specific branch, with
``` bash
git checkout branchname
```
Please replace "branchname" with an existing branch for example "develop". 
Therefore, you type
``` bash
git checkout develop
```
If it worked well, you can tell by the console entry, which should look like that:
``` bash
pi@raspberrypi ~/gateway (develop)>
```
Assuming you work some days later on the project, you have to make sure that you are always up to date on the newest changes. Therefore, type 
``` bash
git pull
```
All changes are shown in console. If no changes are done, you get
``` bash
Already up to date.
```