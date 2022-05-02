from binascii import hexlify # built-in

@staticmethod
def process_data_8(bytes, scale, rate):
    """Parse acceleration data with an resolution of 8 Bit.
    :param bytes: Samples from bytearray
    :type bytes: bytes
    :param scale: Sensor specific scale
    :type scale: int
    :param rate: Sensor specific sampling rate.
    :type rate: int
    :return: x_vector, y_vector, z_vector, timestamp_list
    :rtype: list
    """
    j = 0
    pos = 0
    x_vector = list()
    y_vector = list()
    z_vector = list()
    timestamp_list = list()
    time_between_samples = 1 / rate
    if (scale == 2):
        # logger.info("Scale: 2G")
        faktor = 16 / (256 * 1000)
    elif (scale == 4):
        # logger.info("Scale: 4G")
        faktor = 32 / (256 * 1000)
    elif (scale == 8):
        # logger.info("Scale: 8G")
        faktor = 64 / (256 * 1000)
    elif (scale == 16):
        # logger.info("Scale: 16G")
        faktor = 192 / (256 * 1000)
    while (pos < len(bytes)):
        """Read and store timestamp. This is little endian again"""
        t = bytes[pos:pos + 8]
        inv_t = t[::-1]
        timestamp = int(hexlify(inv_t), 16) / 1000
        pos += 8
        """Read values"""
        for i in range(96):
            value = bytes[pos] << 8
            pos += 1
            if (value & 0x8000 == 0x8000):
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value
            value *= faktor
            if j % 3 == 0:
                x_vector.append(value)
            if j % 3 == 1:
                y_vector.append(value)
            if j % 3 == 2:
                z_vector.append(value)
                timestamp_list.append(timestamp)
                timestamp += time_between_samples
            j += 1
    return x_vector, y_vector, z_vector, timestamp_list

@staticmethod
def process_data_10(bytes, scale, rate):
    """Parse acceleration data with an resolution of 10 Bit.
    :param bytes: Samples from bytearray
    :type bytes: bytes
    :param scale: Sensor specific scale
    :type scale: int
    :param rate: Sensor specific sampling rate.
    :type rate: int
    :return: x_vector, y_vector, z_vector, timestamp_list
    :rtype: list
    """
    j = 0
    pos = 0
    koords = ["\nx", "y", "z"]
    x_vector = list()
    y_vector = list()
    z_vector = list()
    timestamp_list = list()
    time_between_samples = 1 / rate
    if (scale == 2):
        faktor = 4 / (64 * 1000)
    elif (scale == 4):
        faktor = 8 / (64 * 1000)
    elif (scale == 8):
        faktor = 16 / (64 * 1000)
    elif (scale == 16):
        faktor = 48 / (64 * 1000)
    while (pos < len(bytes)):
        t = bytes[pos:pos + 8]
        inv_t = t[::-1]
        timestamp = int(hexlify(inv_t), 16) / 1000
        pos += 8
        for i in range(24):
            value = bytes[pos] & 0xc0
            value |= (bytes[pos] & 0x3f) << 10
            pos += 1
            value |= (bytes[pos] & 0xc0) << 2
            if (value & 0x8000 == 0x8000):
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value
            value *= faktor
            if j % 3 == 0:
                x_vector.append(value)
            if j % 3 == 1:
                y_vector.append(value)
            if j % 3 == 2:
                timestamp_list.append(timestamp)
                timestamp += time_between_samples
                z_vector.append(value)
            j += 1
            value = (bytes[pos] & 0x30) << 2
            value |= (bytes[pos] & 0x0f) << 12
            pos += 1
            value |= (bytes[pos] & 0xf0) << 4
            if (value & 0x8000 == 0x8000):
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value
            value *= faktor
            if j % 3 == 0:
                x_vector.append(value)
            if j % 3 == 1:
                y_vector.append(value)
            if j % 3 == 2:
                timestamp_list.append(timestamp)
                timestamp += time_between_samples
                z_vector.append(value)
            j += 1
            value = (bytes[pos] & 0x0c) << 4
            value |= (bytes[pos] & 0x03) << 14
            pos += 1
            value |= (bytes[pos] & 0xfc) << 6
            if (value & 0x8000 == 0x8000):
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value
            value *= faktor
            if j % 3 == 0:
                x_vector.append(value)
            if j % 3 == 1:
                y_vector.append(value)
            if j % 3 == 2:
                timestamp_list.append(timestamp)
                timestamp += time_between_samples
                z_vector.append(value)
            j += 1
            value = (bytes[pos] & 0x03) << 6
            pos += 1
            value |= (bytes[pos]) << 8
            pos += 1
            if (value & 0x8000 == 0x8000):
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value
            value *= faktor
            if j % 3 == 0:
                x_vector.append(value)
            if j % 3 == 1:
                y_vector.append(value)
            if j % 3 == 2:
                timestamp_list.append(timestamp)
                timestamp += time_between_samples
                z_vector.append(value)
            j += 1
    return x_vector, y_vector, z_vector, timestamp_list

@staticmethod
def process_data_12(bytes, scale, rate):
    """Parse acceleration data with an resolution of 12 Bit.
    :param bytes: Samples from bytearray
    :type bytes: bytes
    :param scale: Sensor specific scale
    :type scale: int
    :param rate: Sensor specific sampling rate.
    :type rate: int
    :return: x_vector, y_vector, z_vector, timestamp_list
    :rtype: list
    """
    j = 0
    pos = 0
    x_vector = list()
    y_vector = list()
    z_vector = list()
    timestamp_list = list()
    time_between_samples = 1 / rate
    if (scale == 2):
        # logger.info("Scale: 2G")
        faktor = 1 / (16 * 1000)
    elif (scale == 4):
        # logger.info("Scale: 4G")
        faktor = 2 / (16 * 1000)
    elif (scale == 8):
        # logger.info("Scale: 8G")
        faktor = 4 / (16 * 1000)
    elif (scale == 16):
        # logger.info("Scale: 16G")
        faktor = 12 / (16 * 1000)
    while (pos < len(bytes)):
        t = bytes[pos:pos + 8]
        inv_t = t[::-1]
        timestamp = int(hexlify(inv_t), 16) / 1000
        pos += 8
        for i in range(48):
            value = bytes[pos] & 0xf0
            value |= (bytes[pos] & 0x0f) << 12
            pos += 1
            value |= (bytes[pos] & 0xf0) << 4
            if (value & 0x8000 == 0x8000):
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value
            value *= faktor
            if j % 3 == 0:
                x_vector.append(value)
            if j % 3 == 1:
                y_vector.append(value)
            if j % 3 == 2:
                timestamp_list.append(timestamp)
                timestamp += time_between_samples
                z_vector.append(value)
            j += 1
            value = (bytes[pos] & 0x0f) << 4
            pos += 1
            value |= bytes[pos] << 8
            pos += 1
            if (value & 0x8000 == 0x8000):
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value
            value *= faktor
            if j % 3 == 0:
                x_vector.append(value)
            if j % 3 == 1:
                y_vector.append(value)
            if j % 3 == 2:
                timestamp_list.append(timestamp)
                timestamp += time_between_samples
                z_vector.append(value)
            j += 1
    return x_vector, y_vector, z_vector, timestamp_list


@staticmethod
def unpack8(self, bytes, samplingrate, scale, csvfile):
    """unpacks the 8 byte sequences of the sensor to hex-strings
    :param bytes: the bytes from your sensor
    :type bytes: bytes
    :param samplingrate: current samplingrate of the sensor
    :type samplingrate: int
    :param scale: current scale of the sensor
    :type scale: int
    """
    j = 0
    pos = 0
    accvalues = [0, 0, 0]
    timestamp = 0
    timeBetweenSamples = 1000/samplingrate
    if(scale == 2):
        faktor = 16/(256*1000)
    elif(scale == 4):
        faktor = 32/(256*1000)
    elif(scale == 8):
        faktor = 64/(256*1000)
    elif(scale == 16):
        faktor = 192/(256*1000)
    while(pos < len(bytes)):
        # Ein Datenblock bei 8 Bit Auflösung ist 104 Bytes lang
        # Jeder Datenblock beginnt mit einem Zeitstempel
        if pos % 104 == 0:
            timestamp = int.from_bytes(
                bytes[pos:pos+7], byteorder='little', signed=False)
            pos += 8
            j = 0
        value = bytes[pos] << 8
        pos += 1
        if(value & 0x8000 == 0x8000):
            # negative Zahl
            # 16Bit Zweierkomplement zurückrechnen
            value = value ^ 0xffff
            value += 1
            # negieren
            value = -value
        # save value
        accvalues[j] = value * faktor
        # Write to CSV
        if(csvfile != None and j % 3 == 2):
            if(csvfile != None):
                csvfile.write("%d;%f;%f;%f\n" % (
                    timestamp, accvalues[0], accvalues[1], accvalues[1]))
            else:
                logger.info("%d;%f;%f;%f\n" %
                    (timestamp, accvalues[0], accvalues[1], accvalues[1]))
            timestamp += timeBetweenSamples
            j = 0
        else:
            j += 1


@staticmethod
def unpack10(self, bytes, samplingrate, scale, csvfile):
    """unpacks the 10 byte sequences of the sensor to hex-strings
    :param bytes: the bytes from your sensor
    :type bytes: bytes
    :param samplingrate: current samplingrate of the sensor
    :type samplingrate: int
    :param scale: current scale of the sensor
    :type scale: int
    """
    i = 0
    j = 0
    pos = 0
    accvalues = [0, 0, 0]
    timestamp = 0
    timeBetweenSamples = 1000/samplingrate
    if(scale == 2):
        faktor = 4/(64*1000)
    elif(scale == 4):
        faktor = 8/(64*1000)
    elif(scale == 8):
        faktor = 16/(64*1000)
    elif(scale == 16):
        faktor = 48/(64*1000)
    while(pos < len(bytes)-1):
        # Ein Datenblock bei 10 Bit Auflösung ist 128 Bytes lang
        # Jeder Datenblock beginnt mit einem Zeitstempel
        if pos % 128 == 0:
            timestamp = int.from_bytes(
                bytes[pos:pos+7], byteorder='little', signed=False)
            pos += 8
            i = 0
            j = 0
        else:
            if i == 0:
                value = bytes[pos] & 0xc0
                value |= (bytes[pos] & 0x3f) << 10
                pos += 1
                value |= (bytes[pos] & 0xc0) << 2
                i += 1
            elif i == 1:
                value = (bytes[pos] & 0x30) << 2
                value |= (bytes[pos] & 0x0f) << 12
                pos += 1
                value |= (bytes[pos] & 0xf0) << 4
                i += 1
            elif i == 2:
                value = (bytes[pos] & 0x0c) << 4
                value |= (bytes[pos] & 0x03) << 14
                pos += 1
                value |= (bytes[pos] & 0xfc) << 6
                i += 1
            elif i == 3:
                value = (bytes[pos] & 0x03) << 6
                pos += 1
                value |= (bytes[pos]) << 8
                pos += 1
                i = 0
            if(value & 0x8000 == 0x8000):
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value
            # save value
            accvalues[j] = value * faktor
            j += 1
            # Write to CSV
            if(j == 3):
                if(csvfile != None):
                    csvfile.write("%d;%f;%f;%f\n" % (
                        timestamp, accvalues[0], accvalues[1], accvalues[2]))
                else:
                    logger.info("%d;%f;%f;%f" %
                        (timestamp, accvalues[0], accvalues[1], accvalues[2]))
                timestamp += timeBetweenSamples
                j = 0

@staticmethod
def unpack12(self, bytes, samplingrate, scale, csvfile):
    """unpacks the 12 byte sequences of the sensor to hex-strings
    :param bytes: the bytes from your sensor
    :type bytes: bytes
    :param samplingrate: current samplingrate of the sensor
    :type samplingrate: int
    :param scale: current scale of the sensor
    :type scale: int
    """
    i = 0
    j = 0
    pos = 0
    accvalues = [0, 0, 0]
    timestamp = 0
    timeBetweenSamples = 1000/samplingrate
    if(scale == 2):
        faktor = 1/(16*1000)
    elif(scale == 4):
        faktor = 2/(16*1000)
    elif(scale == 8):
        faktor = 4/(16*1000)
    elif(scale == 16):
        faktor = 12/(16*1000)
    while(pos < len(bytes)-1):
        # Ein Datenblock bei 12 Bit Auflösung ist 152 Bytes lang
        # Jeder Datenblock beginnt mit einem Zeitstempel
        if pos % 152 == 0:
            timestamp = int.from_bytes(
                bytes[pos:pos+7], byteorder='little', signed=False)
            pos += 8
            i = 0
            j = 0
        else:
            if i == 0:
                value = bytes[pos] & 0xf0
                value |= (bytes[pos] & 0x0f) << 12
                pos += 1
                value |= (bytes[pos] & 0xf0) << 4
                i += 1
            elif i == 1:
                value = (bytes[pos] & 0x0f) << 4
                pos += 1
                value |= bytes[pos] << 8
                pos += 1
                i = 0
            if(value & 0x8000 == 0x8000):
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value
            # save value
            accvalues[j] = value * faktor
            j += 1
            # Write to CSV
            if(j == 3):
                if(csvfile != None):
                    csvfile.write("%d;%f;%f;%f\n" % (
                        timestamp, accvalues[0], accvalues[1], accvalues[2]))
                else:
                    logger.info("%d;%f;%f;%f" %
                        (timestamp, accvalues[0], accvalues[1], accvalues[2]))
                timestamp += timeBetweenSamples
                j = 0