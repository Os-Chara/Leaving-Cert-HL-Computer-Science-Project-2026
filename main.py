from machine import Pin, ADC
import time
from oled_1inch3 import OLED_1inch3 #driver code for the OLED display
import dht
import network
import socket
import secrets                      #imports a private file containing my network SSID and password for privacy

SSID = secrets.SSID                 #name of wifi network - can type information directly into these variables, but for privacy I have not
PASSWORD = secrets.PASSWORD         #wifi password

#defines all my varibales and GPIO pins
OLED = OLED_1inch3()
d= dht.DHT22(Pin(18))
soil_ADC = ADC(26)
warning_light = Pin(27, Pin.OUT)
buzzer = Pin(28, Pin.OUT)
weights = {'temp':0.4, 'humid':0.3, 'moist':0.3}

#creates a blank csv file with the 3 variables as the headings
with open("sensor_data.csv", "w") as file: 
        
        file.write("temperature, humidity, moisture\n")
        
def get_cap():
    RelativeMoisture = (soil_ADC.read_u16())*(100/65535)
    RelativeMoisture = 100 - RelativeMoisture
    return RelativeMoisture   

def get_temp():
    d.measure()
    temp = d.temperature()    
    return temp
    
def get_humidity():
    d.measure()
    humidity = d.humidity()
    return humidity
def WARNINGhigh():
    warning_light.on()
    buzzer.on()
    time.sleep(0.5)
    warning_light.off()
    buzzer.off()
    time.sleep(0.2)
def WARNINGmid():
    warning_light.on()
    time.sleep(0.3)
    warning_light.off()
    time.sleep(0.5)
    
def riskFactor(temp, humid, moist):
    t = (1.2**(temp - 17.5))/10      #formula borrowed from model
    t = max(0, min(1, t))            #clamps the value between 0 and 1
    
    h = (0.93**(humid - 70))/20      #exponential decay formula - risk drops exponentially the higher the air humidity
    h = max(0, min(1, h))
    
    m = (1.14 ** (63 - moist)) / 10
    m = max(0, min(1, m))            #clamps the values between 0 and 1 - removes the negative portion of the function
   
    riskLevel = (t * weights['temp']) + (h * weights['humid']) +  (m  * weights['moist']) #creates a weighted average of the 3 varibales
    return riskLevel

def log_sensor_data():
    temp = round(get_temp(), 3)
    humid = round(get_humidity(), 3)
    moist = round(get_cap(), 3)
    with open("sensor_data.csv", "a") as file:   
        file.write("{},{},{}\n".format(temp,humid,moist))


OLED.fill(0x0000)
OLED.text("connecting..." , 15,30,OLED.white)  #creates a connecting menu while attempting to connect to wifi network
OLED.show()

wlan = network.WLAN(network.STA_IF)  #creates a connection to the wireless chip on the pico
wlan.active(True)                    #turns on the wifi
wlan.connect(SSID, PASSWORD)         #connects to the network using the variables inputed above

while not wlan.isconnected():        #pauses code until network is successfully connected
    time.sleep(1)

ip = wlan.ifconfig()[0]              #stores the ip address given by the network as a variable
#print("Connected:", ip)

# start server
addr = socket.getaddrinfo(ip, 80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(1)

print("Server running")

while True:
    temp = get_temp()
    humid =  get_humidity()
    moist = get_cap()
    wildfireRisk = riskFactor(temp,humid, moist)
    
    if wildfireRisk > 0.8:     #if risk is high alarms and lights activate
        WARNINGhigh()
    elif wildfireRisk > 0.6:   #if risk is medium just the lights activate
        WARNINGmid()
    else:
        warning_light.off()    #low risk turns both off
        buzzer.off()
        
    OLED.fill(0x0000)          #creates a continuously updating display showing current conditions
    OLED.text("Humidity: " + str(round(humid,1)) + "%", 5,4,OLED.white)
    OLED.text("Temp: "+ str(round(temp,1)) + " C" ,5,20,OLED.white)    
    OLED.text("Moisture: "+ str(round(moist,1)) + "%",5,35,OLED.white)
    OLED.text("FireRisk: "+str(round(wildfireRisk,2)),5,50,OLED.white)
    
    OLED.show()
    
    log_sensor_data() #logs the data to the csv file
    
               
    server.settimeout(0.3)
    try:
        client, addr = server.accept()
        request = client.recv(1024)  #recieves up to 1024 bytes from the computer
        with open("sensor_data.csv", "r") as f:
            data = f.read()

        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n" #creates the header for a http response
        response += data                                                 #appends the sensor data to the response

        client.send(response)                                            #sends response back to the computer
        client.close()                                                   #closes the connection once the data is sent
    except OSError:
        pass
        