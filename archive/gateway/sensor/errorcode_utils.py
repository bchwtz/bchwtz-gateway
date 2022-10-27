def ri_error_to_string(error):
    """Decodes the Tag error, if it was raised.

    :param error: Error value in hex.
    :type error: byte
    :return: Result with decoded error code
    :rtype: set
    """
    result = set()
    if (error == 0):
        result.add("RD_SUCCESS")
    elif(error == 1):
        result.add("RD_ERROR_INTERNAL")
    elif(error == 2):
        result.add("RD_ERROR_NO_MEM")
    elif(error == 3):
        result.add("RD_ERROR_NOT_FOUND")
    elif(error == 4):
        result.add("RD_ERROR_NOT_SUPPORTED")
    elif(error == 5):
        result.add("RD_ERROR_INVALID_PARAM")
    elif(error == 6):
        result.add("RD_ERROR_INVALID_STATE")
    elif(error == 7):
        result.add("RD_ERROR_INVALID_LENGTH")
    elif(error == 8):
        result.add("RD_ERROR_INVALID_FLAGS")
    elif(error == 9):
        result.add("RD_ERROR_INVALID_DATA")
    elif(error == 10):
        result.add("RD_ERROR_DATA_SIZE")
    elif(error == 11):
        result.add("RD_ERROR_TIMEOUT")
    elif(error == 12):
        result.add("RD_ERROR_NULL")
    elif(error == 13):
        result.add("RD_ERROR_FORBIDDEN")
    elif(error == 14):
        result.add("RD_ERROR_INVALID_ADDR")
    elif(error == 15):
        result.add("RD_ERROR_BUSY")
    elif(error == 16):
        result.add("RD_ERROR_RESOURCES")
    elif(error == 17):
        result.add("RD_ERROR_NOT_IMPLEMENTED")
    elif(error == 18):
        result.add("RD_ERROR_SELFTEST")
    elif(error == 19):
        result.add("RD_STATUS_MORE_AVAILABLE")
    elif(error == 20):
        result.add("RD_ERROR_NOT_INITIALIZED")
    elif(error == 21):
        result.add("RD_ERROR_NOT_ACKNOWLEDGED")
    elif(error == 22):
        result.add("RD_ERROR_NOT_ENABLED")
    elif(error == 31):
        result.add("RD_ERROR_FATAL")
    return result