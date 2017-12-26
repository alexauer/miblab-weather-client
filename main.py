import logging
import json
import time
import process 

## create logger
logging.basicConfig(format="%(asctimes)s:%(levelname)s:%(message)s", filename="/logs/sensor.log", level=logging.ERROR)

## load config data form config.json
with open('config.json') as config_file:
    config = json.load(config_file)

print("Client started.")

while True:

    if process.check_connectivity(config["connectionModul"]) == False:
        logging.error('Not connected to ' + config["connectionModul"])

    payload = process.prepare_message(config)

    tries = 0

    while tries < 3:

        try:
            response = process.send_message(config,payload)

            if(response["command"]["resend"]):
                tries += 1
                logging.error("Server placed a resend. Response: " + response)
            else:
                break
        except:
            logging.error("Connection lost. No response from server.")
            pass
        else:
            break
    ## sleep
    time.sleep(config["sendInterval"]-180)