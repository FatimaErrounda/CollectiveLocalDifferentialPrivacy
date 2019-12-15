# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 20:57:19 2018

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


MAEValues = []
MREValues = []
RMSEValues = []



budgets = []
count = 0
MAEDistance = []
RMSDistance = []
MREDistance = []

RandomVectorValues = ['0', '1', 'truth']
RRparameter = 1.0 /( numpy.exp(windowepsilon/(2.0*WindowSize)) + 1.0)
RandomVectorProbability =  [RRparameter, RRparameter, 1.0 - 2.0*RRparameter]
indexSlidingWindow = -1
lastrelease = streamCounts[0]
budgets.append(windowepsilon/WindowSize)
lastreleaseindex = 0
count = 1
firststep = 1
secondstep = firststep + WindowSize - 1
Threshold = 2

while count < len(streamCounts):
    slidingWindow = streamCounts[firststep:secondstep]
    totalnumberofreleases = 0
    for timestamp in slidingWindow:
        distanceToLastRelease = count - lastreleaseindex
        if(abs(timestamp-streamCounts[lastreleaseindex]) >= Threshold):
            rrResponse = numpy.random.choice(RandomVectorValues,1, True, RandomVectorProbability)
            if(rrResponse == '1' or (rrResponse == 'truth')):
                if(distanceToLastRelease < WindowSize-1):
                    remainingtimestamps = (WindowSize - distanceToLastRelease)
                    ramainingBudget = (0.5*windowepsilon) - budgets[lastreleaseindex]
                    timestampbudgetForward = ramainingBudget / remainingtimestamps
                else:
                    ramainingBudget = 0.5*windowepsilon
                    timestampbudgetForward = ramainingBudget/WindowSize
                indexSlidingWindow = count-WindowSize +1
                if(WindowSize < count):
                    budgetsum = numpy.sum(budgets[indexSlidingWindow:count])
                    ramainingBudgetBackward = ((0.5*windowepsilon) - budgetsum)/2.0
                else:
                    ramainingBudgetBackward = timestampbudgetForward
                timestampbudget = min(timestampbudgetForward, ramainingBudgetBackward)
                scale = 1./timestampbudget
                noisycount = numpy.random.laplace(timestamp,scale)
                NoiseDistance = abs(noisycount-timestamp)
                MAEDistance.append(NoiseDistance)
                MREDistance.append(NoiseDistance*timestamp)
                RMSDistance.append(NoiseDistance*NoiseDistance)
                lastreleaseindex = count
                budgets.append(timestampbudget)
            else:
                NoiseDistance = abs(streamCounts[lastreleaseindex]-timestamp)
                MAEDistance.append(NoiseDistance)
                MREDistance.append(NoiseDistance*timestamp)
                RMSDistance.append(NoiseDistance*NoiseDistance)
                budgets.append(0.)
        else:
            NoiseDistance = abs(streamCounts[lastreleaseindex]-timestamp)
            MAEDistance.append(NoiseDistance)
            MREDistance.append(NoiseDistance*timestamp)
            RMSDistance.append(NoiseDistance*NoiseDistance)
            budgets.append(0.)
            
        count += 1
    firststep = secondstep
    secondstep = min(firststep + WindowSize,len(streamCounts))

MAEValue = numpy.sum(MAEDistance)/count
MREValue = numpy.sum(MREDistance)/count
RMSEValue = numpy.sqrt(numpy.sum(RMSDistance)/count)
print('the MAE is ',MAEValue)
print('the RMS is ', MREValue)
print('the RMS is ', RMSEValue)

f.close()
