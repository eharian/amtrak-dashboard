from flask import Flask, jsonify, request
from flask_cors import CORS
import os.path
from csv import reader, writer
import statistics
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot
import sys
matplotlib.use('Agg')

DELAY = []

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/delay': {'origins': '*'}})

def init(data):
    data.path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/"
    data.amtrakData = data.path + "/Amtrak master.csv"
    data.master = []

    data.stationType = {}
    data.stationOrder = {}
    data.stationDistances = {}

    data.delayDict = {}

def readAmtrakData():
    with open(data.amtrakData, newline = "") as csvfile:
        amtrakReader = reader(csvfile)
        for row in amtrakReader:
            data.master.append(row)

def generateStationType():
    stationType = {}
    for index, row in enumerate(data.master):
        if index == 0: continue
        currentTrain = int(row[0])
        currentStation = row[2]
        currentType = row[3]
        currentTuple = (currentStation, currentTrain)
        if currentTuple not in stationType:
            stationType[currentTuple] = {currentType}
        else: stationType[currentTuple].add(currentType)

    outputArray = []
    for station in stationType:
        stationName = station[0]
        trainNumber = station[1]
        currentType = stationType[station]
        if len(currentType) == 2: currentType = "A/D"
        else: currentType = str(list(currentType)[0])
        outputArray.append([stationName, trainNumber, currentType])
    with open(data.path + "stationTypes.csv", "w", newline = "") as csvfile:
        amtrakWriter = writer(csvfile)
        amtrakWriter.writerow(["Station", "Train Number", "Arrive/Depart"])
        for row in outputArray:
            amtrakWriter.writerow(row)

def readStationType():
    with open(data.path + "stationTypes.csv", newline = "") as csvfile:
        stationTypeReader = reader(csvfile)
        for index, row in enumerate(stationTypeReader):
            if index == 0: continue
            data.stationType[(row[0], int(row[1]))] = row[2]
 
def readStationOrder():
    with open(data.path + "stationOrder.csv", newline = "") as csvfile:
        stationOrderReader = reader(csvfile)
        for index, row in enumerate(stationOrderReader):
            if index == 0: continue
            data.stationOrder[int(row[0])] = row[1:]
    # print(data.stationOrder)

def getStationDistances():
    stationDistances = {}
    for order in data.stationOrder:
        for i in range(len(data.stationOrder[order])):
            for j in range(len(data.stationOrder[order])):
                station1 = data.stationOrder[order][i]
                station2 = data.stationOrder[order][j]
                distance = abs(i-j)
                key = f'{order}-{station1}-{station2}'
                stationDistances[key] = distance
    with open(data.path + "stationDistances.csv", "w", newline = "") as csvfile:
        amtrakWriter = writer(csvfile)
        amtrakWriter.writerow(["Segment", "Distance"])
        for row in stationDistances:
            amtrakWriter.writerow([row, stationDistances[row]])

def readStationDistances():
    with open(data.path + "stationDistances.csv", newline = "") as csvfile:
        stationDistanceReader = reader(csvfile)
        for index, row in enumerate(stationDistanceReader):
            if index == 0: continue
            data.stationDistances[row[0]] = int(row[1])

def pullDelays():
    for index, row in enumerate(data.master):
        if index == 0: continue
        currentTrain = int(row[0])
        if currentTrain >= 1000 and currentTrain < 2000: continue
        currentStation = row[2]
        currentDiff = int(row[6])
        currentType = row[3]
        currentTuple = (currentStation, currentTrain)
        referenceType = data.stationType[currentTuple]
        if referenceType == "A/D" and currentType == "D": continue  
        if currentTuple not in data.delayDict:
            data.delayDict[currentTuple] = [currentDiff]
        else: data.delayDict[currentTuple].append(currentDiff)

def computeMeanDelay():
    meanDiffs = {}
    for station in data.delayDict:
        averageDiff = statistics.mean(data.delayDict[station])
        meanDiffs[station] = averageDiff
    # for delay in meanDiffs:
    #     print(delay, meanDiffs[delay])
    with open(data.path + "/Output/meanDelays.csv", "w", newline = "") as csvfile:
        amtrakWriter = writer(csvfile)
        amtrakWriter.writerow(["Station", "Train Number", "Difference"])
        for delay in meanDiffs:
            amtrakWriter.writerow([delay[0], delay[1], meanDiffs[delay]])

def getDelayMatrix():
    delayMatrix = {}
    referenceTimes = {}
    prevOrigin = None

    for index, row in enumerate(data.master):
        if index == 0: continue
        currentTrain = int(row[0])
        if currentTrain >= 1000 and currentTrain < 2000: continue 
        currentStation = row[2]
        currentDiff = int(row[6])
        currentOrigin = row[1]
        currentDatetime = datetime.strptime(currentOrigin.split(" ")[0], "%Y-%m-%d")
        currentWeekday = currentDatetime.weekday()
        currentActualDatetime = datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S")
        currentScheduledDatetime = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
        currentType = row[3]
        currentTuple = (currentStation, currentTrain)
        referenceType = data.stationType[currentTuple]

        # reset referenceTimes for new train runs
        if currentOrigin != prevOrigin: referenceTimes = {}

        if referenceType == "A/D" and currentType == "D": continue  
        
        if len(referenceTimes) > 0:
            for station in referenceTimes:
                stationSet = str(currentTrain) + "-" + station + "-" + currentStation
                if stationSet not in delayMatrix:
                    delayMatrix[stationSet] = [(referenceTimes[station][0],
                                               currentDiff, currentWeekday, referenceTimes[station][1], currentScheduledDatetime)]
                else:
                    delayMatrix[stationSet].append((referenceTimes[station][0],
                                               currentDiff, currentWeekday, referenceTimes[station][1], currentScheduledDatetime))
        referenceTimes[currentStation] = [int(currentDiff),currentScheduledDatetime, currentActualDatetime]
        prevOrigin = currentOrigin

    with open(data.path + "/Output/delayMatrix.csv", "w", newline = "") as csvfile:
        amtrakWriter = writer(csvfile)
        amtrakWriter.writerow(["Segment", "Diff 1", "Diff 2", "Weekday", "Sch1", "Sch2"])
        for segment in delayMatrix:
            for diffs in delayMatrix[segment]:
                amtrakWriter.writerow([segment, diffs[0], diffs[1], diffs[2], diffs[3], diffs[4]])

def writeDelayMatrix(segment, splitType, segmentDataPoints):
    standardHeaders = ["Diff 1", "Diff 2"]
    weekdayHeaders = standardHeaders + ["Weekday"]
    headers = {"regression": standardHeaders, "weekday": weekdayHeaders,
               "cdf": standardHeaders}

    filepath = f'{data.path}/Delay Matrices/{splitType}/{segment}.csv'
    with open(filepath, "w", newline = "") as csvfile:
        amtrakWriter = writer(csvfile)
        amtrakWriter.writerow(headers[splitType])
        for datapoint in segmentDataPoints: amtrakWriter.writerow(datapoint)

def splitDelayMatrix(splitType):
    currentSegment, prevRow = None, [[]]
    
    segmentData = []
    segmentSch2 = None 

    with open(data.path + "/Output/delayMatrix.csv", newline = "") as csvfile:
        segmentReader = reader(csvfile)
        for index, row in enumerate(segmentReader):
            if index == 0: continue
            
            currentSegment = row[0]
            
            if currentSegment != prevRow[0] and prevRow[0] != []:
                segmentSch2 = [prevRow[-1]]
                segmentData = [segmentSch2] + segmentData
                writeDelayMatrix(prevRow[0], splitType, segmentData)
                # print( index / 8386062)
                segmentData = []

            appendData = [row[1], row[2]]
            if splitType == "weekday": appendData += [row[3]]
            

            segmentData.append(appendData)
            prevRow = row

    segmentSch2 = [prevRow[-1]]
    segmentData = [segmentSch2] + segmentData
    writeDelayMatrix(prevRow[0], splitType, segmentData)

def getMarginalDelay():
    delayMargins = {}

    segmentAverageMargins = []

    prevOrigin = None
    prevDiff = None
    prevStation = None

    for index, row in enumerate(data.master):
        if index == 0: continue
        currentTrain = int(row[0])
        if currentTrain >= 1000 and currentTrain < 2000: continue 
        currentStation = row[2]
        currentDiff = int(row[6])
        currentOrigin = (row[1], currentTrain)
        currentType = row[3]
        currentTuple = (currentStation, currentTrain)
        referenceType = data.stationType[currentTuple]

        if referenceType == "A/D" and currentType == "D": continue  

        if currentOrigin == prevOrigin:
            if currentStation not in data.stationOrder[currentTrain]: continue
            orderIndex = data.stationOrder[currentTrain].index(currentStation)
            correctPairing = (data.stationOrder[currentTrain][orderIndex - 1],
                              data.stationOrder[currentTrain][orderIndex])
            if (prevStation, currentStation) != correctPairing:
                prevStation = currentStation
                prevOrigin = currentOrigin
                prevDiff = currentDiff
                continue

            margin = currentDiff - prevDiff
            segment = str(currentTrain) + "-" + prevStation + "-" + currentStation
            if segment not in delayMargins:
                delayMargins[segment] = [margin]
            else:
                delayMargins[segment].append(margin)
        prevStation = currentStation
        prevOrigin = currentOrigin
        prevDiff = currentDiff

    for segment in delayMargins:
        segmentAverage = statistics.mean(delayMargins[segment])
        segmentAverageMargins.append([segment, segmentAverage])

    # print(delayList)
    # print(delayMargins)
    # print(segmentAverageMargins)

    with open(data.path + "/Output/delaySegments.csv", "w", newline = "") as csvfile:
        amtrakWriter = writer(csvfile)
        amtrakWriter.writerow(["Segment", "Average Change in Delay"])
        for segment in segmentAverageMargins:
            amtrakWriter.writerow(segment)

def amtrakCorrelations():
    delayMatrixDict = {}
    delayCorrArr = []
    with open(data.path + "/Output/delayMatrix.csv", newline = "") as csvfile:
        correlationReader = reader(csvfile)
        for index, row in enumerate(correlationReader):
            if index == 0: continue
            currentSegment = row[0]
            if currentSegment in delayMatrixDict:
                delayMatrixDict[currentSegment][0].append(int(row[1]))
                delayMatrixDict[currentSegment][1].append(int(row[2]))
            else:
                delayMatrixDict[currentSegment] = [[int(row[1])], [int(row[1])]]
    
    for segment in delayMatrixDict:
        segmentCorr = np.corrcoef(delayMatrixDict[segment][0],
                                  delayMatrixDict[segment][1])[0][1]
        delayCorrArr.append([segment, segmentCorr])
    
    with open(data.path + "/Output/delayCorrelations.csv", "w", newline = "") as csvfile:
        amtrakWriter = writer(csvfile)
        amtrakWriter.writerow(["Segment", "Delay Correlation"])
        for segment in delayCorrArr:
            amtrakWriter.writerow(segment)

def combineSegmentsCorrelations():
    delayCorrelations = {}
    combinationOutput = []
    with open(data.path + "/Output/delayCorrelations.csv", newline = "") as csvfile:
        correlationReader = reader(csvfile)
        for index, row in enumerate(correlationReader):
            if index == 0: continue
            delayCorrelations[row[0]] = row[1]
    with open(data.path + "/Output/delaySegments.csv", newline = "") as csvfile:
        segmentReader = reader(csvfile)
        for index, row in enumerate(segmentReader):
            if index == 0: continue
            currentSegment = row[0]
            if currentSegment in delayCorrelations:
                currentCorrelation = delayCorrelations[currentSegment]
                combinationOutput.append([currentSegment, row[1], currentCorrelation])
    with open(data.path + "/Output/delayAnalysis.csv", "w", newline = "") as csvfile:
        amtrakWriter = writer(csvfile)
        amtrakWriter.writerow(["Segment", "Average Change in Delay", "Delay Correlation"])
        for segment in combinationOutput:
            amtrakWriter.writerow(segment)

def weekdayAnalysis(trainNumber, station):
    weekdayDelays = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    for index, row in enumerate(data.master):
        if index == 0: continue
        currentTrain, currentStation = int(row[0]), row[2]

        if currentTrain != int(trainNumber): continue
        if currentStation != station: continue
        currentType = row[3]
        currentTuple = (currentStation, currentTrain)
        referenceType = data.stationType[currentTuple]
        if referenceType == "A/D" and currentType == "D": continue
        currentDiff = int(row[6])
        currentDate = row[5]
        currentDatetime = datetime.strptime(currentDate.split(" ")[0], "%Y-%m-%d")
        currentWeekday = currentDatetime.weekday()
        weekdayDelays[currentWeekday].append(currentDiff)

    for weekday in weekdayDelays:
        weekdayArray = weekdayDelays[weekday]
        if weekdayArray != []:
            print(weekday, statistics.mean(weekdayArray))

def regressSegment():
    seg1 = []
    seg2 = []
    testSeg1 = []
    testSeg2 = []
    regressErrors = 0
    baselineErrors = 0
    with open(data.path + "/Amtrak Data CSV/laxbur.csv", newline = "") as csvfile:
        correlationReader = reader(csvfile)
        for index, row in enumerate(correlationReader):
            if index == 0: continue
            seg1Int, seg2Int = int(row[0]), int(row[1])
            if index % 5 < 2:
                testSeg1.append(seg1Int)
                testSeg2.append(seg2Int)
            else:
                seg1.append(seg1Int)
                seg2.append(seg2Int)
        x = np.array(seg1).reshape(-1, 1)
        y = np.array(seg2)
        model = LinearRegression().fit(x, y)
        print("Coefficient of Determination:", model.score(x, y))
        intercept = model.intercept_
        slope = model.coef_[0]
        print("Intercept:", intercept)
        print("Slope:", slope)

    for i, point in enumerate(testSeg1):
        actual = testSeg2[i]
        prediction = intercept + slope * point
        error = abs(prediction - actual)
        regressErrors += error
        baselineErrors += abs(point - actual)
    print("Regression Total Error:", regressErrors)
    print("Baseline Total Error:", baselineErrors)

def regressSegmentWeekly(data, train_id, segment, *args):
    testSeg1 = []
    testSeg2 = []
    testSegWeekday = []

    seg1X = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    seg2Y = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

    seg1 = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    seg2 = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

    seg1Regular = []
    seg2Regular = []

    regressErrors = 0
    regressWeeklyErrors = 0
    regressSpecialErrors = 0
    baselineErrors = 0

    originStation = segment.split("-")[1]
    arrivalStation = segment.split("-")[-1]

    weekdayLabels = ["Monday: 0", "Tuesday: 1", "Wednesday: 2", "Thursday: 3",
                     "Friday: 4", "Saturday: 5", "Sunday: 6"]

    filepath = f'{data.path}/Delay Matrices/weekday/individualDelayMatrices/{segment}.csv'

    with open(filepath, newline = "") as csvfile:
        correlationReader = reader(csvfile)
        for index, row in enumerate(correlationReader):
            if index <= 1: continue
            seg1Int, seg2Int, weekday = int(row[0]), int(row[1]), int(row[2])
            seg1X[weekday].append(seg1Int)
            seg2Y[weekday].append(seg2Int)
    for day in seg1X:
        for i, point in enumerate(seg1X[day]):
            if i % 2 == 0:
                testSeg1.append(point)
                testSeg2.append(seg2Y[day][i])
                testSegWeekday.append(day)
            else:
                seg1[day].append(point)
                seg2[day].append(seg2Y[day][i])

                seg1Regular.append(point)
                seg2Regular.append(seg2Y[day][i])

    # print(len(testSeg1))
    # print(len(testSeg2))
    # print(len(seg1[0]))
    # print(len(seg2[0]))

    # for day in seg1:
    #     if seg1[day] == []: continue
    #     std = statistics.stdev(seg1[day])
    #     mean = statistics.mean(seg1[day])
    #     for i, point in enumerate(seg1[day]):
    #         z = abs((point - mean) / std)
    #         if z > 3:
    #             seg1[day].pop(i)
    #             seg2[day].pop(i)

    # std = statistics.stdev(seg1Regular)
    # mean = statistics.mean(seg1Regular)
    # for i, point in enumerate(seg1Regular):
    #     z = abs((point - mean) / std)
    #     if z > 3:
    #         seg1Regular.pop(i)
    #         seg2Regular.pop(i)


    intercepts = [None, None, None, None, None, None, None]
    slopes = [None, None, None, None, None, None, None]
    weekdayCount = 0

    for day in seg1:
        if len(seg1[day]) <= 1: continue
        # print("Regressing on day", day)
        x = np.array(seg1[day]).reshape(-1, 1)
        y = np.array(seg2[day])
        model = LinearRegression().fit(x, y)
        # print("Coefficient of Determination:", model.score(x, y))
        intercept = model.intercept_
        slope = model.coef_[0]
        # print("Intercept:", intercept)
        # print("Slope:", slope)  
        intercepts[day] = intercept
        slopes[day] = slope

        weekdayCount += 1

    # print("seg1X", seg1X)
    # print("seg2Y", seg2Y)
    # print("seg1", seg1)
    # print("seg2", seg2)
    # print("seg1Regular", seg1Regular)
    # print("seg2Regular", seg2Regular)
    # print("intercepts", intercepts)
    # print("slopes", slopes)
    # print("testSeg1", testSeg1)
    # print("testSeg2", testSeg2)
    # print("testSegWeekday", testSegWeekday)

    # print(intercepts, slopes) 
    # print(testSeg1)

    #regular regression
    if len(seg1Regular) < 1:
        return [segment, "0", "0", "0", "0"]
    x = np.array(seg1Regular).reshape(-1, 1)
    y = np.array(seg2Regular)
    model = LinearRegression().fit(x, y)
    intercept = model.intercept_
    slope = model.coef_[0]

    count = 0
    accurateWeekly = 0
    accurateRegular = 0
    accurateSpecial = 0
    baselineAccurate = 0

    for i, point in enumerate(testSeg1):
        weekday = testSegWeekday[i]
        # if weekday != 2: continue
        actual = testSeg2[i]
        if weekdayCount > 1 and slopes[weekday] != None:
            predictionWeekly = intercepts[weekday] + slopes[weekday] * point
        else:
            predictionWeekly = intercept + slope * point
        prediction = intercept + slope * point
        # specialPrediction = specialReg([seg1Regular, seg2Regular], point)
        # if specialPrediction == None: specialPrediction = prediction


        errorWeekly = abs(predictionWeekly - actual)
        error = abs(prediction - actual)
        # errorSpecial = abs(specialPrediction - actual)
        errorBaseline = abs(point - actual)
        regressWeeklyErrors += errorWeekly
        regressErrors += error
        # regressSpecialErrors += errorSpecial
        baselineErrors += errorBaseline

        if error < 5: accurateRegular += 1
        if errorWeekly < 5: accurateWeekly += 1
        if errorBaseline < 5: baselineAccurate += 1 
        # if errorSpecial < 5: accurateSpecial += 1
        count += 1

    

    if len(args) == 1:
        modelSelector = {}
        modelSelection = "Regular"

        with open(data.path + "/Delay Matrices/accuracyAnalysisV1.csv", newline = "") as csvfile:
            accuraciesReader = reader(csvfile)
            for i, row in enumerate(accuraciesReader):
                if i == 0: continue
                modelSelector[row[0]] = row[5]

        if segment in modelSelector:
            modelSelection = modelSelector[segment]
        if modelSelection == "Baseline":
            return segmentHistogram(data, segment, args[0], args[0])
        elif modelSelection == "Weekday":
            for day in seg1:
                if day != []:
                    print(weekdayLabels[day])
            selectedWeekday = int(input("Enter weekday of origin departure: "))
            y = intercepts[selectedWeekday] + slopes[selectedWeekday] * x
            testSeg1 = seg1[selectedWeekday]
            testSeg2 = seg2[selectedWeekday]
            predictedDelay = intercepts[selectedWeekday] + slopes[selectedWeekday] * int(args[0])
        else:
            y = intercept + slope * x
            predictedDelay = intercept + slope * int(args[0])
        # print("Regression Weekly Total Error:", regressWeeklyErrors)
        # print("Regression Total Error:", regressErrors)
        # print("Regression Special Error:", regressSpecialErrors)
        # print("Baseline Total Error:", baselineErrors)

        # print("Regression Weekly Accuracy:", accurateWeekly / count)
        # print("Regression Accuracy:", accurateRegular / count)
        # print("Regression Special Accuracy", accurateSpecial / count)
        # print("Baseline Accuracy:", baselineAccurate / count)
       
        matplotlib.pyplot.plot(testSeg1, testSeg2, 'ro')
        matplotlib.pyplot.plot(x, y)
        matplotlib.pyplot.title(f"{originStation}-{arrivalStation} On-Time Performance Across All Runs")
        matplotlib.pyplot.xlabel(f"Minutes Delay at {originStation} (earlier station)")
        matplotlib.pyplot.ylabel(f"Minutes Delay at {arrivalStation} (latter station)")
        matplotlib.pyplot.savefig(f"../client/src/assets/images/{train_id}.png")
        #matplotlib.pyplot.show()

        #return predictedDelay
        #print("Delay Estimate:", predictedDelay)
        #return segmentHistogram(data, segment, args[0], int(predictedDelay))
    elif len(args) == 2:
        if args[0] == "Weekday":
            outputAccuracy = str(accurateWeekly)
        elif args[0] == "Baseline":
            outputAccuracy = str(baselineAccurate)
        else: 
            outputAccuracy = str(accurateRegular)
        return(segment, outputAccuracy, count)
    else:
        return [segment, str(accurateRegular),
        str(accurateWeekly),
        str(baselineAccurate),
        str(count)]

def segmentHistogram(data, segment, originDelay, regressionEstimate):
    timeLabelsSeg1 = []
    timeLabelsSeg2 = []
    seg1Delays = []
    seg2Delays = []

    maxClip = 100

    regressionEstimate = int(regressionEstimate)

    pdf = {}

    filepath = f'{data.path}/Delay Matrices/cdf/{segment}.csv'
    with open(filepath) as csvfile:
        segmentReader = reader(csvfile)
        for index, row in enumerate(segmentReader):
            if index == 0: continue
            if index == 1: 
                seg2Sch = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                # seg2Sch = datetime.strptime(row[0], "%m/%d/%Y %H:%M")
                continue

            # seg1Sch =  datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
            

            # seg1Sch =  datetime.strptime(row[4], "%m/%d/%Y %H:%M")

            currentSeg1Delay = int(row[0])
            seg1Delays.append(currentSeg1Delay)
            if abs(currentSeg1Delay - int(originDelay)) < 10:
                currentSeg2Delay = int(row[1])
                seg2Delays.append(currentSeg2Delay)
            
            # actualOriginDT = seg1Sch + timedelta(minutes = originDelay)
            # actualOriginText = actualOriginDT.strftime("%#I:%M \n%p")
            seg2SchEstimate = seg2Sch + timedelta(minutes = regressionEstimate)

    
    minSeg2 = min(seg2Delays)
    xLowerBound = minSeg2
    
    clippedDataSeg1 = np.clip(seg1Delays, None, 100)

    maxClip = minSeg2 + 100
    clippedDataSeg2 = np.clip(seg2Delays, None, maxClip)

    clippedDataSeg2.sort()
    print(clippedDataSeg2)
    maxSeg2 = clippedDataSeg2[-1]
    if xLowerBound + 100 < maxSeg2:
        xUpperBound = xLowerBound + 100
    else:
        xUpperBound = maxSeg2
    dataSeg2Len = len(clippedDataSeg2)

    timeIncr = int((xUpperBound - xLowerBound) // 10) + 1
    allowableIncrements = len(range(xLowerBound, xUpperBound, timeIncr)) 

    # for increment in range(10):
    #     currentTrancheSeg1 =  seg1Sch + timedelta(minutes = increment * 10)
        
    #     if increment != 9:
    #         timeLabelsSeg1.append(currentTrancheSeg1.strftime("%#I:%M \n%p"))
            
    #     else:
    #         timeLabelsSeg1.append(currentTrancheSeg1.strftime("%#I:%M \n%p+"))
            
    for increment in range(allowableIncrements):
        currentTrancheSeg2 = seg2Sch + timedelta(minutes = minSeg2) + timedelta(minutes = increment * timeIncr)
        if increment != allowableIncrements - 1:
            timeLabelsSeg2.append(currentTrancheSeg2.strftime("%#I:%M \n%p"))
        else:
            timeLabelsSeg2.append(currentTrancheSeg2.strftime("%#I:%M \n%p+"))

    print(timeLabelsSeg1)
    print("Length of Seg 2 Time Labels:", len(timeLabelsSeg2), timeLabelsSeg2)
    tickLocations = list(range(xLowerBound, xUpperBound, timeIncr))
    print("Length of Tick Locations:", len(tickLocations), tickLocations)

    # bins = range(0,110,10)
    # fig1, ax1 = matplotlib.pyplot.subplots()
    # ax1.hist(clippedDataSeg1, bins, histtype='bar',
    #                        weights=np.ones(len(clippedDataSeg1)) / len(clippedDataSeg1))

    # ax1.set_xticks(range(0,100,10))
    # ax1.set_xticklabels(timeLabelsSeg1)
    # ax1.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1))
    # leaveV = ax1.axvline(int(originDelay), c = 'r')
    # ax1.legend((leaveV,), ("Left at " + actualOriginText,))
    # # fig1.show()

    # fig2, ax2 = matplotlib.pyplot.subplots()
    # hist2 = ax2.hist(clippedDataSeg2, bins, histtype='bar',
    #                        weights=np.ones(len(clippedDataSeg2)) / len(clippedDataSeg2))

    # ax2.set_xticks(tickLocations)
    # ax2.set_xticklabels(timeLabelsSeg2)
    # ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1))

    # fig2.show()

    for trainDelay in clippedDataSeg2:
        if trainDelay not in pdf:
            pdf[trainDelay] = 1 / dataSeg2Len
        else:
            pdf[trainDelay] += 1 / dataSeg2Len

    cdf = []
    cdfXVals = []
    cumulation = 0
    for trainDelay in pdf:
        cumulation += pdf[trainDelay]
        cdf.append(cumulation)
        cdfXVals.append(trainDelay)

    fig3, ax3 = matplotlib.pyplot.subplots()
    fig3.subplots_adjust(top = 0.8, bottom = 0.15)
    ax3.plot(cdfXVals, cdf)
    arrivalStation = segment.split("-")[-1]
    originalStation = segment.split("-")[1]
    titleText = f'''Probability of arriving at {arrivalStation} Station by various times\n
    given {originDelay}-minute delay at {originalStation} Station
    '''
    ax3.title.set_text(titleText)
    ax3.set_xlabel('Arrival by')
    ax3.set_xticks(range(xLowerBound, xUpperBound, timeIncr))
    ax3.set_xticklabels(timeLabelsSeg2)
    ax3.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1))
    intersectionY = regressionPointInterceptor(regressionEstimate, cdfXVals, cdf)
    intersectionSch = regressionPointInterceptor(0, cdfXVals, cdf)
    probStr = str(round(intersectionY * 100, 1))
    probSch = str(round(intersectionSch * 100, 1)) 
    arriveV = ax3.vlines(regressionEstimate, 0, intersectionY, colors = "red", linestyles = 'dashed')
    schV = ax3.vlines(0, 0, intersectionSch, colors = "blue", linestyles = 'dotted')
    arriveX = ax3.hlines(intersectionY, tickLocations[0], regressionEstimate, colors = "red", linestyles = 'dashed')
    schX = ax3.hlines(intersectionSch, tickLocations[0], 0, colors = "blue", linestyles = 'dotted')
    ax3.legend((arriveV, schV),
               (seg2SchEstimate.strftime("%#I:%M %p") + " Predicted ETA at " + str(probStr) + "% likelihood",
                seg2Sch.strftime("%#I:%M %p") + " Scheduled ETA at " + str(probSch) + "% likelihood"),
                loc = "lower right")
    ax3.set_xlim(left = tickLocations[0], right = tickLocations[-1])
    ax3.set_ylim(bottom = 0, top = 1)
    fig3.show()

def regressionPointInterceptor(targetX, cdfXVals, cdf):
    if targetX < cdfXVals[0]: return 0
    x1, y1, x2, y2 = None, None, None, None
    for i in range(len(cdfXVals) - 1):
        x1 = cdfXVals[i]
        x2 = cdfXVals[i + 1]
        y1 = cdf[i]
        y2 = cdf[i + 1]
        if x2 > targetX: 
            return (((y2 - y1) / (x2 - x1)) * (targetX - x1)) + y1
    return y2

def specialReg(trainingData, delay):
    subset = [[], []]
    pointCount = 0
    for i, datapoint in enumerate(trainingData[0]):
        differential = abs(datapoint - int(delay))
        if differential < 5:
            subset[0].append(datapoint)
            subset[1].append(trainingData[1][i])
            pointCount += 1

    # print(subset)
    print("Delay Input", delay)
    print(subset[0])
    if pointCount < 2:
        print("Not enough points")
        return None
    xSpec = np.array(subset[0]).reshape(-1, 1)
    ySpec = np.array(subset[1])
    modelSpec = LinearRegression().fit(xSpec, ySpec)
    interceptSpec = modelSpec.intercept_
    slopeSpec = modelSpec.coef_[0]

    # print("intercept", intercept, "slope", slope)
    prediction = interceptSpec + slopeSpec * int(delay)
    print(prediction)

    return prediction

def regressionAccuracyTest():
    record = False
    existing = set()

    for file in os.listdir(data.path + "/Delay Matrices/"):
        if file == "accuracy.csv": record = True
    if record:
        with open(data.path + "/Delay Matrices/accuracy.csv", newline = "") as csvfile:
            accuraciesReader = reader(csvfile)
            for row in accuraciesReader:
                existing.add(row[0] + ".csv")

    filepath = f'{data.path}/Delay Matrices/weekday/'
    with open(data.path + "/Delay Matrices/accuracy.csv",'a', newline = "") as csvfile:
        amtrakWriter = writer(csvfile)
        for file in os.listdir(filepath):
            if file in existing: continue
            # print(file)
            results = regressSegmentWeekly(data, train_id, file.split(".")[0])
            amtrakWriter.writerow(results)

def regressionComparisonTest():
    poi = []
    with open(data.path + "/Delay Matrices/accuracyV2.csv", newline = "") as csvfile:
        accuraciesReader = reader(csvfile)
        for row in accuraciesReader:
            segment = row[0]
            regCount = int(row[1])
            weekCount = int(row[2])
            baseCount = int(row[3])
            totalCount = int(row[4])
            if totalCount == 0: continue
            if segment not in data.stationDistances: continue
            distance = data.stationDistances[segment]

            propReg = regCount / totalCount
            propWeek = weekCount / totalCount
            propBase = baseCount / totalCount

            propArray = [(propReg, "Regular"),
                         (propWeek, ("Weekday")),
                         (propBase, "Baseline")]
            propArray.sort(key = lambda x: x[0])
            advantage = propArray[-1][0] - propArray[1][0]
            if advantage > 0.05:
                poi.append([segment] + propArray +[distance, propArray[-1][1], advantage])
    with open(data.path + "/Delay Matrices/accuracyAnalysis.csv",'w', newline = "") as csvfile:
        amtrakWriter = writer(csvfile)
        amtrakWriter.writerow(["Segment", "PropReg", "PropWeek", "PropBase", "Distance", "Winner", "Margin"])
        for row in poi:
            amtrakWriter.writerow(row)

def multimodalRegressionAccuracyTest():
    record = False
    existing = set()
    modelSelector = {}

    with open(data.path + "/Delay Matrices/accuracyAnalysis.csv", newline = "") as csvfile:
        accuraciesReader = reader(csvfile)
        for i, row in enumerate(accuraciesReader):
            if i == 0: continue
            modelSelector[row[0]] = row[5]

    for file in os.listdir(data.path + "/Delay Matrices/"):
        if file == "accuracyMultiModal.csv": record = True
    if record:
        with open(data.path + "/Delay Matrices/accuracyMultiModal.csv", newline = "") as csvfile:
            accuraciesReader = reader(csvfile)
            for row in accuraciesReader:
                existing.add(row[0] + ".csv")

    filepath = f'{data.path}/Delay Matrices/weekday/'
    with open(data.path + "/Delay Matrices/accuracyMultiModal.csv",'a', newline = "") as csvfile:
        amtrakWriter = writer(csvfile)
        for file in os.listdir(filepath):
            if file in existing: continue
            # print(file)
            segment = file.split(".")[0]
            modelSelection = "Regular"
            if segment in modelSelector:
                modelSelection = modelSelector[segment]
            results = regressSegmentWeekly(data, train_id, segment, modelSelection, True)
            amtrakWriter.writerow(results)

def amtrak_analysis(input_value):
    class Struct(object): pass
    data = Struct()
    init(data)
    train_id = input_value['train_id'].strip(' ')
    train_deets = input_value['train_id'].strip(' ') + '-' + input_value['source'].strip(' ') + '-' + input_value['dest'].strip(' ')
    time = int(input_value['delay_time'])
    regressSegmentWeekly(data, train_id, train_deets, time)

@app.route('/delay', methods=['GET', 'POST'])
def get_delay():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        train_id = post_data.get('train_id').strip(' ')
        source = post_data.get('source')
        dest = post_data.get('dest')
        time = post_data.get('delay_time')
        DELAY.append({
            'train_id': train_id,
            'source': source,
            'dest': dest,
            'delay_time': time
        })
        amtrak_analysis(DELAY[-1])
        response_object['delay'] = f'src/assets/images/{train_id}.png'
    else:
        response_object['delay'] = DELAY
    return jsonify(response_object)
    


if __name__ == '__main__':
    app.run()