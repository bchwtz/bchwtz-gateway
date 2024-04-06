# Raspberry Pi

This chapter gives an overview on how to set up the raspberry pi from scratch.

## Raspberry Pi OS Install
Documentation follows this video: https://www.youtube.com/watch?v=rGygESilg8w

4. Take the SD-card of the Raspberry and put it in the card reader of your PC.

5. Go to https://www.raspberrypi.com/software/ and download the Raspberry Pi OS Imager if not yet installed.

6. Open Raspberry Pi Imager.

7. Install operating system and choose the Raspberry Pi OS (normally recommended).

8. Choose your SD card as storage and click "WRITE".   
9. After the process has finished boot up the Raspberry Pi with the SD-card.

## Enable SSH on Raspberry Pi
Now there are two different methods to activate SSH and VNC for your Raspberry Pi, one using the terminal while the other uses the GUI.  
1. Connect your Raspberry Pi to a screen via Micro HDMI if you have an external screen.  
2. Connect your Raspberry to your WiFi
### Enable SSH (Method 1)
Run the following command to access the configuration:
```{bash, eval=F}
sudo raspi-config
```
Here choose _Interface_Options_, select SSH and then set VNC (not necessarily needed).

### Enable SSH (Method 2)
Activate SSH and VNC by clicking on the raspberry on the top left -> Preferences -> Raspberry-Pi-Configuration->Interfaces, change SSH and VNC to activated

![](./imgs/Raspberry_setup1.PNG)

![](./imgs/Raspberry_setup2.PNG)


## Set up PuTTY and finalize connection to Raspberry Pi
9. On your PC, download PuTTY (https://www.putty.org/) or use any other ssh tool.
10. Get your Raspberry’s IP-Adress by opening a command line on your PC and and type 
```{bash, eval=F}
ping raspberrypi.local
```
11. Open PuTTY, type the IP-Adress into the Host Name field. You can save it by entering a name into the “Saved Sessions” field and pressing “save”. Afterwards select “open”.

12. When asked for the username type 
```{bash, eval=F}
pi
```
and afterwards enter your password. If you did not change it on Raspberry’s startup it should be 
```{bash, eval=F}
raspberry
```

13. To clone the Gateway repository (https://github.com/bchwtz-fhswf/gateway) onto your pi, you need a SSH Key which is connected to your account. Generate it by following the instructions in https://docs.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent for Linux (you dont have to pass it to a key agent) and add it to your account by following the instructions in https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account 

14. Clone the gateway repository to your raspberry by typing 
```{bash, eval=F}
git clone git@github.com:bchwtz-fhswf/gateway.git
```
into the PuTTY window connected to your raspberry. When asked, enter the SSH Key password you initiated while generating the key.

READ THE [DEVELOPMENT PRINCIPLES](global_architecture/development_principles.md) FOR THIS PROJECT - ALL COMMITS NOT COMPLYING WILL BE DELETED IMMEDIATLY!
