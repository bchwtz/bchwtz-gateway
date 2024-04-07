# Sensor
![](imgs/systemarchitecture-highlevel.png)

This Chapter is a short guide for setting up your development environment. Until you receive your hardware you can start with installing the necessary software.

## Software Setup

1. Download “Segger Embedded Studio for ARM 5.10d” (https://www.segger.com/downloads/embedded-studio)

2. Download nRF5_SDK_15.3.0_59ac345.zip (https://developer.nordicsemi.com/nRF5_SDK/nRF5_SDK_v15.x.x/)

3. Generate a new SSH keypair for GitHub (if you have not already done so at one point in the past already). You need this key in order to clone all necessary files from GitHub. On Linux you can do it like this (more information can be found [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)):
```{bash, eval=F}
ssh-keygen -t ed25519 -C "your_email@example.com"
```

4. Add the newly created public key to GitHub (see [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account))

5. Clone https://github.com/bchwtz-fhswf/ruuvi.firmware.c (If you wanted to get started with Git: look at [this](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository) link or search on google/youtube). The following command will create a new folder in the current directory with the name of the repository:
```{bash, eval=F}
git clone https://github.com/bchwtz-fhswf/ruuvi.firmware.c
```
6. Copy the folder from extracting the ZIP in step 2 into the 'ruuvi.firmware.c' folder. It should look like this:
git clone https://github.com/bchwtz-fhswf/ruuvi.firmware.c
![](./imgs/nRF_in_Ruuvi_folder.png)
7. Open the cloned directory in a terminal window and update and sync all submodules:
```{bash, eval=F}
make pull
```
8. Open SEGGER and click “File” -> “Open Solution”, navigate to the cloned repository and open “ruuvi.firmware.c/src/ruuvi.firmware.c.emProject”. The project should now be opened inside SEGGER.

9. Search “Project ‘ruuvitag_b’” on the left inside SEGGER, right-click and choose “Set as Active Project”.

## Alternative Software Setup (building releases)

1. Install docker (either docker-desktop or on linux your preferred docker package).

2. If you use Windows or Mac, please set your preferred RAM-size and CPU-Count in the docker-desktop-app.

3. Run `docker_build.sh` in any bash-compatible environment (e.g. [git-bash](https://gitforwindows.org/))

This leaves you with the release-binaries in `src/targets/ruuvitag_b/arm_gcc/`.
For further details refer to the [README.md](https://github.com/bchwtz-fhswf/ruuvi.firmware.c#using-the-build-toolchain-inside-docker-recommended-way)

## Hardware Setup

6. Open your ruuvi tag, take PCB & battery out (you can do so with a little screwdriver or by gently pulling on the battery clip)
![](./imgs/Tag_Demontage.jpg)
7. Connect the “Tag Connector” cable + plug to your ruuvi tag
![](./imgs/Tag_connector.jpg)
8. Connect the other side of the tag connector to the Debug out slot on the Nordic SDK
9. Connect your SDK over USB with your PC
![](./imgs/SDK_SetUp.jpg)

10. Turn on the switch at the bottom left

11. To test if everything is right, open SEGGER and click “Target”->”Connect J-Link”. SEGGER should connect to your SDK

12. To flash your ruuvi tag with the cloned firmware, click “Target”->”Erase All”, afterwards click “Build”->”Build and Run” 

READ THE [DEVELOPMENT PRINCIPLES](global_architecture/development_principles.md) FOR THIS PROJECT - ALL COMMITS NOT COMPLYING WILL BE DELETED IMMEDIATLY!
