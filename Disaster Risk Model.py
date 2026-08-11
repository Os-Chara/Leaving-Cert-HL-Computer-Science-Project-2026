import csv
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
import requests
from statistics import mean

url = "http://192.168.68.171/"   #IP address of the pico on network
FalseStart = True
selected_data = "sensorData.csv" #variable containing the chosen csv

risk_list = []
tempList = []
humidList = []
moistList = []

rawTemp = []
rawHumid = []
rawMoist = []

WI1Temp = []
WI1TempRisk = []
WI1risk = []

WI2Humid = []
WI2HumidRisk =[]
WI2Moist = []
WI2MoistRisk = []
WI2risk = []

#dictionaries
labelsFont = {'family':'serif','color':'black','fontsize':10}    #font used in graph labels
titlesFont = {'family':'serif','color':'black','fontsize':15}    #font used in graph titles
weights = {'temp':0.4, 'humid':0.3, 'moist':0.3}                 #how each variable is weighed

def tempRisk(temp):
    risk = (1.2**(temp - 17.5))/10    #risk exponentially increases above 17.5 degrees
    return max(0, min(1, risk))       #returns risk as a value between 0 and 1

def humidityRisk(humid):            #inverts value
    h = (0.93**(humid - 70))/20       #exponential decay formula - risk drops exponentially the higher the air humidity
    h = max(0, min(1, h)) 
    return h

def moistRisk(moisture):
    m = (1.14 ** (63 - moisture)) / 10
    m = max(0, min(1, m))
    return m

def riskFactor(Temp, Humid, Moist):
    t = tempRisk(Temp)
    h = humidityRisk(Humid)
    m = moistRisk(Moist)
    
    riskLevel = (t * weights['temp']) + (h * weights['humid']) +  (m  * weights['moist']) #creates a weighted average of the 3 varibales
    return riskLevel

def create_3_graph_visualisation(title, x1, overall_risk, temp_risk, humid_risk, moist_risk, no_formula_temp, no_formula_humid, no_formula_moist):
    fig = plt.figure(figsize=(12,6))
    gs = GridSpec(2, 2, figure=fig)   #creates a 2 by 2 grid for the graphs

    ax1 = fig.add_subplot(gs[:,0])    #the first graph will take up the entire left side of the screen
    ax2 = fig.add_subplot(gs[0,1])    #the second will take the top right
    ax3 = fig.add_subplot(gs[1,1])    #the third will go to the bottem left
    fig.suptitle(title, fontdict = titlesFont)
    
    ax1.plot(x1, overall_risk,color='orange', label='Total risk')
    ax1.set_title("'Risk Factor' of wild fires over time", fontdict = labelsFont)
    ax1.set_ylabel("Wild fire risk factor (0-1)", fontdict = labelsFont)
    ax1.legend()
    ax1.set_ylim(0, 1.01)                                                    #limits the y axis to just over 1 as values cannot exceed 1
    ax1.set_xlabel("Time", fontdict = labelsFont)

    ax2.set_title("Relative 'Risk Factor' of wild fire variables over time", fontdict = labelsFont)
    ax2.set_ylabel("Risk factors by variable(0-1)", fontdict = labelsFont)
    ax2.set_xlabel("Time", fontdict = labelsFont)

    ax2.plot(x1-0.2, temp_risk, color='firebrick', label='Temperature')     #plots the 3 individual risk facotrs against each other
    ax2.plot(x1, humid_risk, color='turquoise', label='Humidity')
    ax2.plot(x1+0.2, moist_risk, color='peru', label='Soil Moisture')
    ax2.set_ylim(0, 1.01)

    ax3.set_title("Raw Sensor Values Over Time", fontdict=labelsFont)
    ax3.set_xlabel("Time", fontdict=labelsFont)
    ax3.set_ylabel("Sensor Values", fontdict=labelsFont)

    ax3.plot(x1, no_formula_temp, color='red', label='Temperature (°C)')    #plots the 3 raw values onto the third graph
    ax3.plot(x1, no_formula_humid, color='blue', label='Humidity (%)')
    ax3.plot(x1, no_formula_moist, color='green', label='Moisture (%)')

    ax1.legend(loc='best', fontsize='7.5')  
    ax2.legend(loc='best', fontsize='7.5')
    ax3.legend(loc='best', fontsize='7.5')
    
    ax1.axhspan(0.8, 1.01, color='red', alpha=0.1)       #adds 3 differnt colour zones to the graph
    ax1.axhspan(0.5, 0.8, color='yellow', alpha=0.1)
    ax1.axhspan(0, 0.5, color='green', alpha=0.1)
    ax1.text(0, 0.82, "High Risk Zone", color='red')    #adds lables to the zones
    ax1.text(0, 0.52, "Medium Risk Zone", color='goldenrod')
    ax1.text(0, 0.02, "Low Risk Zone", color='green')
    
    plt.tight_layout()
    plt.show()

while FalseStart:
    DataSelected = int(input("Select data to use:\n\n1 = request new data \n2 = Use last recieved data\n3 = Use collected data\n4 = Use simulated summer day-night dataset\n"))
    if DataSelected == 1:
        print("Requesting data from Pico...")
        try:
            r = requests.get(url, timeout=10) #requests data from the Pico's server, times out after 10s
            r.raise_for_status()
            print("Data received")
            with open("sensorData.csv", "w") as f:
                f.write(r.text)
            FalseStart = False
        except requests.exceptions.RequestException:
            print("Failed to receive data from Pico")
    elif DataSelected == 2:
        print("using last received Data")
        FalseStart = False
    elif DataSelected == 3:
        print("using collected data")
        FalseStart = False
        selected_data = "collectedClassroomData.csv"
    elif DataSelected == 4:
        print("using summer day-night Data")
        FalseStart = False
        selected_data = "summer_day_night_dataset.csv"
    else:
        print("Invalid Selection")

with open(selected_data, newline='') as file:
    reader = csv.DictReader(file)
    for row in reader:
        temp = float(row['temperature'])
        humid = float(row[' humidity'])
        moist = float(row[' moisture'])
        WI1temp = temp + 4
        WI2humid = humid -15
        WI2moist = moist -7.5
        
        rawTemp.append(temp)                                       #creates lists of each of the raw values
        rawHumid.append(humid)
        rawMoist.append(moist)
        
        tempList.append(tempRisk(temp))                            #creates lists of the risks of each variable
        humidList.append(humidityRisk(humid))
        moistList.append(moistRisk(moist))
        
        risk = riskFactor(temp, humid, moist)    
        risk_list.append(round(risk, 3))                           #creates a list containing the overall wild risk values over time                  

        WI1Temp.append(WI1temp)                                    #what if 1: the temperature increases by 4 degrees
        WI1risk.append(round(riskFactor(WI1temp, humid, moist),3))
        WI1TempRisk.append(tempRisk(WI1temp))
        
        WI2Humid.append(WI2humid)                                  #what if 2: drought leads to lower air humidity and soil moisture
        WI2Moist.append(WI2moist)
        WI2HumidRisk.append(humidityRisk(WI2humid))
        WI2MoistRisk.append(moistRisk(WI2moist))
        WI2risk.append(riskFactor(temp, WI2humid, WI2moist))

x1 = np.arange(len(tempList))   #gets the total amount of rows to act as the x axis

#def create_3_graph_visualisation(title, x1, overall_risk, temp_risk, humid_risk, moist_risk, no_formula_temp, no_formula_humid, no_formula_moist):
AsRecieved = ('Wildfire Risk Visualisations', x1, risk_list, tempList, humidList, moistList, rawTemp, rawHumid, rawMoist) #creates a tuple containing the data as recieved 
WhatIf1 = ('What if scenario 1:\nClimate change projection\nAn increase in temperature by 4 degrees', x1, WI1risk, WI1TempRisk, humidList, moistList,WI1Temp, rawHumid, rawMoist) #creates a tuple containing the data for what if 1
WhatIf2 = ('What if scenario 2:\nDrought conditions\nA decrease in air humidity(-15%) and soil moisture(7.5%)',x1, WI2risk, tempList, WI2HumidRisk, WI2MoistRisk, rawTemp, WI2Humid, WI2Moist) 

meanAR = round(mean(risk_list),3)
meanWI1 = round(mean(WI1risk),3)
meanWI2 = round(mean(WI2risk),3)



create_3_graph_visualisation(*AsRecieved) #unpacks the tuple to be graphed
create_3_graph_visualisation(*WhatIf1)
create_3_graph_visualisation(*WhatIf2)

print('\nMean risk of data as received: ', +meanAR)
print('Mean risk of What-If scenario 1: ', +meanWI1)
print('Mean risk of What-If scenario 2: ', +meanWI2)
print('In what if scenario 1, the mean wildfire risk increases by ', + round((meanWI1 - meanAR), 3))
print('In what if scenario 2, the mean wildfire risk increases by ', + round((meanWI2 - meanAR), 3))