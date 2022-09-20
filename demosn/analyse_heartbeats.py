import logging

def calculate_average_times_get_heartbeat():
    count = 0 
    warnings = 0
    info = -2
    with open('get_heartbeat_retries.txt') as f:
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
    
    calculate_average_times_get_heartbeat()



