# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 16:13:19 2018

@author: errounda
"""

import json
import numpy


StreamedData = 'appIot_data_24h.json'

WindowSize = 100
windowepsilon = 1.0

print('reading input', StreamedData)

with open(StreamedData, 'r') as f:
    streamCounts = json.load(f)


#####
#Budget Distribution
#####

firststep = 0
secondstep = firststep + WindowSize

budgets = []
MAEDistance = []
MREDistance = []
RMSDistance = []
count = 0
windowsBudgets = []

while (count < len(streamCounts)):
    slidingWindow = streamCounts[firststep:secondstep]        
    if(firststep == 0 ):
    #must have a release here to compare to
        lastrelease = slidingWindow[0]
    count = firststep
    
    for timestamp in slidingWindow:
        distance = timestamp - lastrelease
        distance = abs(distance)
        distanceScale = (2.0*WindowSize)/windowepsilon
        distance = numpy.random.laplace(distance,distanceScale)
        if(firststep == 0):
            lowerbound = 0
        else:
            lowerbound = count-WindowSize
        budgetsum = numpy.sum(budgets[lowerbound:count])
        remainingBudget = (windowepsilon/2.0) - budgetsum
        scale = 2./remainingBudget
        if distance > scale:
            noisycount = numpy.random.laplace(timestamp,scale)
            NoiseDistance = abs(noisycount-timestamp)
            MAEDistance.append(NoiseDistance)
            MREDistance.append(NoiseDistance*timestamp)
            RMSDistance.append(NoiseDistance*NoiseDistance)
            lastrelease = noisycount
            budgets.append(remainingBudget/2.)
        else:
            NoiseDistance = abs(lastrelease-timestamp)
            MAEDistance.append(NoiseDistance)
            MREDistance.append(NoiseDistance*timestamp)
            RMSDistance.append(NoiseDistance*NoiseDistance)
            budgets.append(0.)
        count += 1
        if(WindowSize < count):
            slidingindex = count-WindowSize +1
            thesum = numpy.sum(budgets[slidingindex:count])
            windowsBudgets.append(thesum)
    firststep = secondstep
    secondstep = min(firststep + WindowSize,len(streamCounts))

MAEValue = numpy.sum(MAEDistance)/count
MREValue = numpy.sum(MREDistance)/count
RMSEValue = numpy.sqrt(numpy.sum(RMSDistance)/count)
print('the MAE is ',MAEValue)
print('the RMS is ', MREValue)
print('the RMS is ', RMSEValue)
f.close()