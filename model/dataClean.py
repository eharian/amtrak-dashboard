import os.path
from csv import writer
from datetime import datetime, timedelta
from copy import deepcopy
import zipfile

def init(data):
    data.path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/"
    data.serviceDisruptionLines = ["* THIS TRAIN EXPERIENCED A SERVICE DISRUPTION.\n",
                                   "* THIS TRAIN HAS EXPERIENCED CANCELLATIONS.\n"]
    data.master = []

    data.stationOrder = {}

def unzipData():
    zipDir = data.path + "Zipped Data/"
    for zippedFile in os.listdir(zipDir):
        with zipfile.ZipFile(zipDir + zippedFile, 'r') as zip_ref:
            zip_ref.extractall(data.path + "data/")

def generateDataTable(dataType):
    dataDir = data.path + "Data/"
    for dirs in os.listdir(dataDir):
        print("************** " + dirs + " **************")
        for files in os.listdir(dataDir + dirs):
            if dataType == "masterData":
                extractData(dataDir + dirs + "/" + files)
            elif dataType == "stationOrder":
                extractStationOrder(dataDir + dirs + "/" + files)
                break

def extractStationOrder(filepath):
    startFlag = False
    filename = filepath.split("/")[-1]
    trainNumber = filename.split("_")[0]
    with open(filepath) as f:
        lines = f.readlines()
        for index, row in enumerate(lines):
            if startFlag == False:
                if row == "* V    V  V     V  V     V     V     V\n":
                    startFlag = True
                continue
            else:
                station = row[2:5].strip(" ")
                if trainNumber not in data.stationOrder:
                    data.stationOrder[trainNumber] = [station]
                else:
                    data.stationOrder[trainNumber].append(station)

def extractData(filepath):
    startFlag = False
    trainFlag = False
    trainStartDateTime = ""

    filename = filepath.split("/")[-1]
    print(filename)
    inputArray = [[]] * 9
    trainNumber = filename.split("_")[0]
    trainStartDay = filename.split("_")[1][:-4]
    # print("Train Start Date:", trainStartDay)
    # print("Train Number:", trainNumber)
    # print(inputArray)
    with open(filepath) as f:
        lines = f.readlines()
        for index, row in enumerate(lines):
            # print(index, row.strip("\n"))
            if startFlag == False:
                if row in data.serviceDisruptionLines:
                    continue
                elif trainFlag == False:
                    trainFlag = True
                    trainName = row[2:].strip("\n")
                elif row == "* V    V  V     V  V     V     V     V\n":
                    startFlag = True
                continue
            # determine the start date of trip for origin station row
            if trainStartDateTime == "":
                trainStartDateTime = parseLine(row, "origin", trainStartDay)
            if row[0] == " ": continue
            inputArray = [[]] * 9
            inputArray[7] = trainName
            inputArray[0] = trainNumber
            inputArray[1] = trainStartDateTime
            parseLine(row, inputArray, trainStartDay)
        f.close()

def parseLine(line, array, startDate):
    depArray = array
    arrArray = deepcopy(array)
    containsDep, containsArr = False, False
    arrDifText, depDifText = "*", "*"

    station = line[2:5].strip(" ")
    arrDay = line[7].strip(" ")
    schArr = line[10:15].strip(" ")
    depDay = line[16].strip(" ")
    schDep = line[19:24].strip(" ")
    actArr = line[25:30].strip(" ")
    actDep = line[31:36].strip(" ")

    # print("Station:", station)
    # print("Arrival Day:", arrDay)
    # print("Scheduled Arrival:", schArr)
    # print("Departure Day:", depDay)
    # print("Scheduled Departure:", schDep)
    # print("Actual Arrival:", actArr)
    # print("Actual Departure:", actDep)

    # used to return the start date time of a train route
    if array == "origin":
        return convertTime(schDep.strip("\n"), startDate, depDay)

    # check if line contains arrival and departure data
    if actArr != "" and actArr[0].isnumeric():
        containsArr = True
        schArr = convertTime(schArr, startDate, arrDay)
        actArr = convertTime(actArr, startDate, arrDay)

        arrArray[2] = station
        arrArray[3] = "A" 
        arrArray[4] = schArr
        arrArray[5] = actArr
        arrArray[8] = arrDay
    if actDep != "" and actDep[0].isnumeric():
        containsDep = True
        schDep = convertTime(schDep, startDate, depDay)
        actDep = convertTime(actDep, startDate, depDay)

        depArray[2] = station
        depArray[3] = "D"    
        depArray[4] = schDep
        depArray[5] = actDep
        depArray[8] = depDay
    if containsArr == True and containsDep == True:
        arrDifText = line[47:74].rstrip(" \n")
        depDifText = line[88:].rstrip(" \n")
        
        arrDif = convertDiff(arrDifText)
        depDif = convertDiff(depDifText)
        
        arrArray[6] = arrDif
        depArray[6] = depDif
        
        data.master.append(arrArray)
        data.master.append(depArray)
        # print(arrArray)
        # print(depArray)
    elif containsArr == True:
        arrDifText = line[47:74].rstrip(" \n")
        arrDif = convertDiff(arrDifText)

        arrArray[6] = arrDif
        
        data.master.append(arrArray)
        # print(arrArray)
    elif containsDep == True:
        depDifText = line[48:74].rstrip(" \n")
        depDif = convertDiff(depDifText)

        depArray[6] = depDif
        
        data.master.append(depArray)
        # print(depArray)

    # print("Arrival Difference:", arrDifText)
    # print("Departure Difference:", depDifText)


    

def convertTime(textTime, startDate, tripDay):
    tripDay = int(tripDay) - 1

    # pad the hour with a leading 0 if needed
    if len(textTime) == 4: textTime = "0" + textTime
    timeStr = startDate + " " + textTime + "M"
    dateTimeObject = datetime.strptime(timeStr, "%Y%m%d %I%M%p")
    dateTimeObject += timedelta(days = tripDay)
    return dateTimeObject

def convertDiff(textDiff):
    timeDiff = 0
    if textDiff == "On time.": return 0
    splitDiff = textDiff.split(" ")
    if len(splitDiff) == 5:
        timeDiff += int(splitDiff[0]) * 60 + int(splitDiff[2])
    elif len(splitDiff) == 3:
        if "minute" in splitDiff[1]: 
            timeDiff += int(splitDiff[0])
        else:
            timeDiff += 60 * int(splitDiff[0])
    if splitDiff[-1] == "early.": timeDiff *= -1
    # print(timeDiff)
    return timeDiff

def writeCSV(dataType):
    with open(data.path + "amtrak.csv", "w", newline = "") as csvfile:
        amtrakWriter = writer(csvfile)
        if dataType == "master":
            amtrakWriter.writerow(["Train Number", "Origin Date",
                                   "Station", "Arrive/Depart", "Scheduled Time",
                                   "Actual Time", "Difference", "Train Name",
                                   "Trip Day"])
            for row in data.master:
                amtrakWriter.writerow(row)
        elif dataType == "stationOrder":
            amtrakWriter.writerow(["Train Number", "Order"])
            for row in data.stationOrder:
                amtrakWriter.writerow([row] + data.stationOrder[row])

if __name__ == "__main__":
    class Struct(object): pass
    data = Struct()
    init(data)
    # generateDataTable("masterData")
    # writeCSV("master")
    generateDataTable("stationOrder")
    writeCSV("stationOrder")