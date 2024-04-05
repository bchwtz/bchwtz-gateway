# Getting Started Package

## Raspbery Pi OS "Buster"

## Board

### Raspberry Pi 4 - Model B

### Compute Model 4

#### Enabling USB Ports

The USB 2.0 ports on the Wavesahre Baseboard A are disabled by default. To enable those ports the following commands need to be added to the end of `/boot/config.txt`.

```{bash, eval=FALSE}
dtoverlay=dwc2,dr_mode=host
```

The system needs to be *rebooted* to make the USB 2.0 ports work.

#### Enabling Camera & DSI Port

```{bash, eval=FALSE}
sudo apt-get install p7zip-full
 wget https://www.waveshare.com/w/upload/4/41/CM4_dt_blob.7z
 7z x CM4_dt_blob.7z -O./CM4_dt_blob
 sudo chmod 777 -R CM4_dt_blob
 cd CM4_dt_blob/
 #If you want to use both cameras and DSI0
 sudo  dtc -I dts -O dtb -o /boot/dt-blob.bin dt-blob-disp0-double_cam.dts
 #If you want to ue both cameras and DSI1
 sudo  dtc -I dts -O dtb -o /boot/dt-blob.bin dt-blob-disp1-double_cam.dts
```
