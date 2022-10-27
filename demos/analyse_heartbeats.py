import logging

def calculate_average_times_get_heartbeat(file_path : str):
    """Calculates a percentage of many tries to get the heartbeat from the tag were successful.
    
    The function reads a specified file and count how many warnigs were thrown when trying to get the 
    heartbeat from the tag. 
    All lines containing INFO give out the heartbeat execpt the first two, which state, that the general connection
    was successful. This is why the info starts counting at -2.

    Arguments:
        file_path (str): The path to where the logging file lies.
    """
    count = 0 
    warnings = 0
    info = -2
    with open(file_path) as f:
       for line in f:
        if 'WARNING' in line:
            warnings += 1
        if 'INFO' in line:
            info += 1
        count += 1
    average_tries = "{:.2f}".format(warnings / info)
    logging.info(f'There were {info} attempts of getting the Heartbeat from the Tag')
    logging.info(f'The amount of tries to accomplish this goal was: {warnings}')
    logging.info(f"It took {average_tries} tries on average to get the Heartbeat.")

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    
    calculate_average_times_get_heartbeat('get_heartbeat_retries.txt')



