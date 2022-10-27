from gateway import hub
from gateway.experimental import flashing

myHub = hub.Hub()

myHub.discover()

for (i, item) in enumerate(myHub.sensorlist,start=0):
    print(i, item.name, item.mac)

intex = input("Choose the sensor you want to flash by entering the element index \
    (Hint: Remember that the tag has to be in Bootloader modus!): ")

SensObj = myHub.sensorlist[item]

file_path = input("Enter the absolute path to your firmware.zip: ")

target_direcory = input("Enter the absolut path to the direcory \
    where the firmware.zip should be unpacked")

dfu = flashing.device_firmware_upgrade(file_path,target_direcory,SensObj)

input("Check if your device is still in Bootloader mode and press enter to continue!")

try:
    dfu.start_flashing_sensor()
except e as exception:
    print("Error occured: {}".format(e))
