import os
import ntplib
import json
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

##  prepare the payload with message and message hash 
def prepare_message(config):

    sense = SenseHat()
    sensor_id = get_serial()
    id_hash = hmac.new(config["hashIDKey"].encode('utf-8'),sensor_id.encode('utf-8'), hashlib.sha256).hexdigest()

    t = sense.get_temperature()
    p = sense.get_pressure()
    h = sense.get_humidity()

    #floating zero format
    t = "{:10.2f}".format(round(t,2))
    p = round(p)
    h = round(h)

    timestamp = 0
    timestamp = round(get_ntp_time(config["ntpServer"]))
    
    msg = {}
    msg = {'sensorID':sensor_id,
           'sensorObjectID':config["sensorObjectID"],
           'sensorIDHash':id_hash,
           'sensorname':config["sensorname"],
           'timestamp':timestamp,
           'weatherData':{
                'temperatureCPU':get_cpu_temp(),
                'temperatureEnvironment':t,
                'pressure':p,
                'humidity':h}}
    
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








