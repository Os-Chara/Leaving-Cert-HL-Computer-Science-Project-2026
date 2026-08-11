import network
import socket
import secrets
import time

SSID = secrets.SSID #name of wifi network
PASSWORD = secrets.PASSWORD #wifi password


wlan = network.WLAN(network.STA_IF) #connects to wireless chip
wlan.active(True)                   #turns on the wifi
wlan.connect(SSID, PASSWORD) #connects to the network using secrets

while not wlan.isconnected(): #pauses code until connected
    time.sleep(1)

ip = wlan.ifconfig()[0] #stores the IP address given by the network
print("Successfully connected, your IP address is:", ip)
