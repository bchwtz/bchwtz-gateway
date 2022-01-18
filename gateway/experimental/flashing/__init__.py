import asyncio
from binascii import hexlify, crc32
from bleak import BleakClient
import time
from gateway import sensor
import logging 
import zipfile # python standard library
import os # python standard library

# Creat a named logger 'log' and set it on INFO level
log = logging.getLogger('dfu_flashing')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
log.addHandler(console_handler)

loop = asyncio.get_event_loop()


interface = sensor.sensor_interface
DFU_CONTROL_POINT = sensor.sensor_interface["communication_channels"]["DFU_CONTROL_POINT"]
DFU_DATA_POINT = sensor.sensor_interface["communication_channels"]["DFU_DATA_POINT"]

def unzip_dfu_file(source_path : str, target_directory : str):
    """Unzip the device firmware update to a given target_directory.

    Args:
        source_path (str): C:\\Path\\to\\your\\zip
        target_directory (str): C:\\destination\\path

    Raises:
        Exception: If an exception occures, will be logged and raised.
    """    
    try:
        with zipfile.ZipFile(source_path, "r") as zip_ref:
            zip_ref.extractall(target_directory)
            zip_ref.close()
    except Exception as e:
        log.error(e)
        raise Exception
    return

def dfu_file_loader(target_directory : str):
    """Load the necessary files from the target directory.

    Args:
        target_directory (str): C:\\dest\\path

    Returns:
        dat_file, bin_file: necessary files
    """    
    for f_name in os.listdir(target_directory):
        if f_name.endswith('.dat'):
            path_to_dat = target_directory + "//" + f_name
            log.info("try load dat")
            with open(path_to_dat, "rb") as f:
                dat_file = f.read()
        elif f_name.endswith('.bin'):
            path_to_bin = target_directory + "//" +f_name
            log.info("try load bin")
            with open(path_to_bin, "rb") as f:
                bin_file = f.read()
        else:
            log.warning('{} was found in directory'.format(f_name))
    return dat_file, bin_file
    

class ErrorBootloaderModus(Exception):
    """Raised when the sensor is not in bootloader modus.

    Args:
        Exception (Custom): "sensor is not in bootloader modus"
    """    
    pass


class FutureHolder():
    """Eventhandler to communicate between sensor and gateway asynchron.

    Returns:
        None
    """    
    future = None

    def __init__(self):
        self.reset()
    
    async def wait(self):
        await self.future

    def reset(self):
        self.future=loop.create_future()
    
    def set_result(self, result):
        self.future.set_result(result)
    
    def set_exception(self, exception):
        self.future.set_exception(exception)

    def result(self):
        return self.future.result()

fh = FutureHolder()


class device_firmware_upgrade():
    def __init__(self,path_to_dfu_zip : str, destination_path_to_unzip : str, s= sensor.sensor("DEFAULT", "DEFAULT")):
        """Initialize the class object device_firmware_upgrade. This class do not search for bluetooth devices. It needs a specific device
        which can be found by the `gateway.hub` module.

        Args:
            path_to_dfu_zip (str): C:\\Path\\to\\your\\zip
            destination_path_to_unzip (str): C:\\Path\\to\\destination
            s (sensor object, optional): The firmware update needs a specific sensor for the connection workflow. Defaults to sensor.sensor("DEFAULT", "DEFAULT").
        """          
        self.sensor = s
        unzip_dfu_file(path_to_dfu_zip, destination_path_to_unzip)
        self.bin_file, self.dat_file = dfu_file_loader(destination_path_to_unzip)
        self.check_boot_loader()

    def check_boot_loader(self):
        """This function checks if the state of a given sensor is 'Bootloader'. If the state does not match, an exception will raised.

        Raises:
            AttributeError: Will be raised if an user tries to initialize an class object with the default sensor object.
            ErrorBootloaderModus: Will be raised if the sensor is not in Bootloader state.
        """        
        if "RuuviBoot" in self.sensor.name:
            log.info("sensor is in bootloader modus")
            return
        elif "DEFAULT" in self.sensor.name:
            raise AttributeError("device_firmware_upgrade can't run with 'default' name")
        else:
            raise ErrorBootloaderModus("sensor is not in bootloader modus")

    def start_flashing_sensor(self):
        """Starts the flashing workflow.
        """        
        loop.run_until_complete(self.updateProcedure(self.sensor.mac))

    async def updateProcedure(self, address : str):
        """Update handler.

        Args:
            adress (str): The mac adress of a sensor.
        """        
        async with BleakClient(address) as client:
            await client.start_notify(DFU_CONTROL_POINT, self.callback)
            
            log.info("set crc intervall to 0")
            result = await self.sendPaket(client, DFU_CONTROL_POINT, bytearray.fromhex("0200000000"))
            
            log.info("send dat file...")
            await self.sendData(client, 1, self.dat_file)

            log.info("send bin file...")
            await self.sendData(client, 2, self.bin_file)

            await client.stop_notify(DFU_CONTROL_POINT)
        log.info("task done and return")
        return
  
    async def sendPaket(self, client, c , data):
        """Preparing the sensor for the firmware update.

        Args:
            client (BleakClient(<address>)): Bleak client
            c ([type]): Interface between sensor and gateway
            data ([type]): data

        Returns:
            [type]: Callbacks
        """        
        fh.reset()
        await client.write_gatt_char(c, data)
        await fh.wait()
        return fh.result()
    
    async def sendData(self, client, obj, data):
        """Main function to send the dfu files

        Args:
            client (BleakClient(<address>)): Bleak client
            obj ([type]): [description]
            data ([type]): .bin- or .dat-file

        Raises:
            Exception: if the crcs do not match to each other, this exception will be raised.
        """        
        log.info("excecute select...")
        result = await self.sendPaket(client, DFU_CONTROL_POINT, bytearray.fromhex("06%02x"%(obj)))
        offset = result["offset"]
        crc = result["crc32"]
        max_size = result["max_size"]
        if offset<len(data):
            log.info("create sending...")
            blocklen = len(data)
            if blocklen>max_size:
                blocklen=max_size
            msg = bytearray.fromhex("01%02x"%(obj))
            msg.extend(int.to_bytes(blocklen, 4, byteorder="little", signed=False))
            result = await self.sendPaket(client, DFU_CONTROL_POINT, msg)

            log.info("data sending...")
            bytecount = 0
            globalbytecount = 0
            for i in range(offset, len(data), 16):
                ende=i+16
                if ende > len(data):
                    ende= len(data)
                msg = data[i:ende]
                await client.write_gatt_char(DFU_DATA, msg)
                crc = crc32(msg, crc)
                bytecount += len(msg)

                if bytecount+len(msg)>max_size:
                    globalbytecount += bytecount
                    bytecount = 0
                    log.info("execute for {} bytes".format(globalbytecount))
                    msg = bytearray.fromhex("04")
                    result = await self.sendPaket(client, DFU_CONTROL_POINT, msg)

                    blocklen = len(data)-globalbytecount
                    if blocklen>max_size:
                        blocklen = max_size
                    msg = bytearray.fromhex("01%02x" %(obj))
                    msg.extend(int.to_bytes(blocklen, 4, byteorder='little', signed=False))
                    result = await self.sendPaket(client, DFU_CONTROL_POINT, msg)
        log.info("request crc")
        msg = bytearray.fromhex("03")
        result = await self.sendPaket(client, DFU_CONTROL_POIN, msg)
        if result["crc32"]!=crc32(data):
            raise Exception("crc values don't match to each other!")
        else:
            log.info("data send successful")
        log.info("execute...")
        msg = bytearray.fromhex("04")
        result = await self.sendPaket(client, DFU_CONTROL_POINT , msg)

    def callback(self, sender : int, value: bytearray):
        """Handles incoming callbacks from the sensor

        Args:
            sender (int): [description]
            value (bytearray): Incoming messages
        """        
        value = value[1:]
        if value[1]==0x01:
            if value[0]==0x06:
                fh.set_result({
                    "max_size": int.from_bytes(value[2:6], byteorder='little', signed=False),
                    "offset": int.from_bytes(value[6:10], byteorder='little', signed=False),
                    "crc32": int.from_bytes(value[10:14], byteorder='little', signed=False)
                })
            elif value[0]==0x03:
                fh.set_result({
                    "offset": int.from_bytes(value[2:6], byteorder='little', signed=False),
                    "crc32": int.from_bytes(value[6:10], byteorder='little', signed=False)                    
                })
            elif value[0]==0x01 or value[0]==0x02 or value[0]==0x04:
                fh.set_result(None)
            else:
                fh.future.set_exception(Exception("unknown message"))
        elif value[1]==0x00: #NRF_DFU_RES_CODE_INVALID
            fh.set_exception(Exception("invalid opcode!"))
        elif value[1]==0x02: #NRF_DFU_RES_CODE_OP_NOT_SUPPORTED
            fh.set_exception(Exception("opcode not supported!"))
        elif value[1]==0x03: #NRF_DFU_RES_CODE_INVALID_PARAMETER
            fh.set_exception(Exception("missing or invalid parameter value!"))
        elif value[1]==0x04: #NRF_DFU_RES_CODE_INSUFFICIENT_RESOURCES
            fh.set_exception(Exception("not enough memory for the data object"))
        elif value[1]==0x05: #NRF_DFU_RES_CODE_INVALID_OBJECT
            fh.set_exception(Exception("data object does not match to the firmware and hardware requirements, the signature is wrong, or parsing the command faild!"))
        elif value[1]==0x07: #NRF_DFU_RES_CODE_UNSUPPORTED_TYPE
            fh.set_exception(Exception("not a valid object type for a create request!"))
        elif value[1]==0x08: #NRF_DFU_RES_CODE_OPERATION_NOT_PERMITTED
            fh.set_exception(Exception("the state of the DFU process does not allow this operation!"))
        elif value[1]==0x0a: #NRF_DFU_RES_CODE_OPERATION_FAILD
            fh.set_exception(Exception("operation faild!"))
        elif value[1]==0x0b: #NRF_DFU_RES_CODE_EXT_ERROR
            fh.set_exception(Exception("extended error. The next byte of the response contains the error code of the extended error!"))


