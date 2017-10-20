import os
import ntplib
import json
import time
import hmac
import requests
import netifaces
import hashlib
from sense_hat import SenseHat 


## get CPU temperature
def get_cpu_temp():
    res = os.popen('vcgencmd measure_temp').readline()
    temp = float(res.replace("temp=", "").replace("'C\n", ""))
    return("{:10.1f}".format(temp))

## ger Raspberry Pi serial number for sensorID                  
def get_serial():
    CPUserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6]=='Serial':
                CPUserial = line[10:26]
        f.close()
    except:
        CPUserial = "ERROR0000000000"
    
    return CPUserial

## request NTP Timestamp from configured NTP server
def get_ntp_time(ntp_server):
    
    ## setup NTP Client
    c = ntplib.NTPClient()
    try:
        ntp_response = c.request(ntp_server,version=3)
        return ntp_response.tx_time
    except:
        return False
        
## checks ethernet connection, returns True if connected 
def check_connectivity(modul):
    addr = netifaces.ifaddresses(modul)
    return netifaces.AF_INET in addr

def get_average_weather_data(avg_steps):

    t=0.
    p=0.
    h=0.

    sense = SenseHat()
    
    for i in range(0,avg_steps):
        
        t += sense.get_temperature()
        p += sense.get_pressure()
        h += sense.get_humidity()
        print(t)
        time.sleep(60)

    t_avg = t/avg_steps
    p_avg = p/avg_steps
    h_avg = h/avg_steps

    print(t_avg)
    return t_avg, p_avg, h_avg

##  prepare the payload with message and message hash 
def prepare_message(config):
    
    timestamp = 0
    timestamp = round(get_ntp_time(config["ntpServer"]))

    sensor_id = get_serial()
    key = str(timestamp)[-4:] + config["hashIDKey"]

    id_hash = hmac.new(key.encode('utf-8'),sensor_id.encode('utf-8'), hashlib.sha256).hexdigest()

    t_avg, p_avg, h_avg = get_average_weather_data(3)
    

    #floating zero format
    t_avg = "{:10.2f}".format(round(t_avg,2))
    p_avg = round(p_avg)
    h_avg = round(h_avg)

    msg = {}
    msg = {'sensorID':sensor_id,
           'sensorObjectID':config["sensorObjectID"],
           'sensorIDHash':id_hash,
           'sensorname':config["sensorname"],
           'timestamp':timestamp,
           'weatherData':{
                'temperatureCPU':get_cpu_temp(),
                'temperatureEnvironment':t_avg,
                'pressure':p_avg,
                'humidity':h_avg}}
    
    ## hash message 
    msg_hash = hmac.new(config["hashMsgKey"].encode('utf-8'), str(json.dumps(msg,separators=(',',':'))).encode('utf-8'), hashlib.sha256).hexdigest()
    
    ## prepare payload
    payload = {"message":msg,"messageHash":msg_hash}

    return(payload)

## send POST request to server
def send_message(config,payload):

    r = requests.post(config["serverIP"]+':'+ config["serverPORT"] +'/sensors/', json = payload)
    response = r.json()
    
    return(response)








