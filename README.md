# Saturn Tower Client
A basic (Python) raspberry pi client for the saturn tower weather station.

### Prerequisites
Client currently tested with Python v3.5.3

Following packages need to be installed.

* time, json, logging, SenseHat, hashlib, netifaces, requests, hmac, ntplib

### Installing

Copy the repository into your prefered folder.

Create a config.json file in the client folder and insert the correct parameters matched to your Node.js weahter server.

```javascript
{
"sensorname":"myFirstSensor",
"sensorObjectID":"MongoDBObjectID",
"sensorID":"mySensorID",
"sendInterval":300,
"hashIDKey":"myHashIDKey",
"hashMsgKey":"myHashMsgKey",
"ntpServer":"myPreferedNTPServer",
"serverIP":"myServerIP",
"serverPORT":"MyServerPORT",
"connectionModul":"myConnectivity(ETH/WIFI)"
}
```

### Usage

This client sends weather data (temperature, pressure and humidity) aquired from a sense hat modul to the server. The connection to the server can be ethernet oder wifi. Communication between server and client is based on REST. Messages are authenticated with HMAC hashing.
