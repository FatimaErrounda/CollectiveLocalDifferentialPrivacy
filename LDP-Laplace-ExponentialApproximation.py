# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 20:57:19 2018

@author: errounda
"""

import json
import numpy


StreamedData = 'appIot_data_24h.json'


print('reading input', StreamedData)

with open(StreamedData, 'r') as f:
    streamCounts = json.load(f)
    
WindowSize =10
windowepsilon = 50.0




# =============================================================================
# the randomized response approach with a new randomized vector 
# at each begining of the sliding window
# =============================================================================

    
budgets = []
count = 0
MAEDistance = []
RMSDistance = []
MREDistance = []
ResponseVector = []
for i in range(WindowSize):
    ResponseVector.append(1)
RandomVectorValues = ['0', '1', 'truth']
RRparameter = 1.0 /( numpy.exp(windowepsilon/(4.0*WindowSize)) + 1.0)
RandomVectorProbability =  [RRparameter, RRparameter, 1.0 - 2.0*RRparameter]
indexSlidingWindow = -1
lastrelease = streamCounts[0]
budgets.append(windowepsilon/WindowSize)
lastreleaseindex = 0
count = 1
firstTime = True
firststep = 1
secondstep = firststep + WindowSize - 1
Threshold = 2
numberoftimesexhaustbudget = 0

ApproximationsHistory = dict()
ApproximationValues = []
ApproximationDistribution = []

while count < len(streamCounts):
    slidingWindow = streamCounts[firststep:secondstep]
    totalnumberofreleases = 0
    if(firstTime == True ):
    #must have a release here to compare to
        firstTime = False
        counter = 1
    else:
        counter = 0
    for timestamp in slidingWindow:
        distanceToLastRelease = count - lastreleaseindex - 1
        if(abs(timestamp-streamCounts[lastreleaseindex]) >= Threshold):
            rrResponse = numpy.random.choice(RandomVectorValues,1, True, RandomVectorProbability)
            if(rrResponse == '1' or (rrResponse == 'truth')):
                if(distanceToLastRelease < WindowSize-1):
                    if(distanceToLastRelease != 0):
                        timestampbudgetForward = distanceToLastRelease*((0.5*windowepsilon)/WindowSize)
                    else:
                        remainingtimestamps = WindowSize + lastreleaseindex-1-count
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
                if timestamp in ApproximationsHistory.keys():
                    distanceToApproximation = abs(ApproximationsHistory[timestamp]-timestamp)
                    if( distanceToApproximation > NoiseDistance):
                        ApproximationsHistory[timestamp] = noisycount
                else:
                    ApproximationsHistory[timestamp] = noisycount
                MAEDistance.append(NoiseDistance)
                MREDistance.append(NoiseDistance*timestamp)
                RMSDistance.append(NoiseDistance*NoiseDistance)
                lastrelease = noisycount
                lastreleaseindex = count
                budgets.append(timestampbudget)
            else:
                utility = dict()
                if(any(ApproximationsHistory)):
                    for key, value in ApproximationsHistory.items():
                        if(value < timestamp + Threshold and value > timestamp - Threshold):
                            utility[value] = numpy.exp((windowepsilon*abs(value-timestamp))/(8.0*WindowSize) )
                    if(any(utility)):
                        utilityNormalization = sum(utility.values())
                        for key, value in sorted(utility.items()):
                            ApproximationValues.append(key)
                            ApproximationDistribution.append(value/utilityNormalization)
                        approximatedValue = numpy.random.choice(ApproximationValues,1, ApproximationDistribution)
                        NoiseDistance = abs(approximatedValue-timestamp)
                    else:
                        NoiseDistance = abs(lastrelease-timestamp)
                else:
                    NoiseDistance = abs(lastrelease-timestamp)
                MAEDistance.append(NoiseDistance)
                RMSDistance.append(NoiseDistance*NoiseDistance)
                MREDistance.append(NoiseDistance*timestamp)
                budgets.append(0.)
        else:
            utility = dict()
            if(any(ApproximationsHistory)):
                for key, value in sorted(ApproximationsHistory.items()):
                    if(value < timestamp + Threshold and value > timestamp - Threshold):
                        utility[value] = numpy.exp((windowepsilon*abs(value-timestamp))/(8.0*WindowSize) )
                if(any(utility)):
                    utilityNormalization = sum(utility.values())
                    for key, value in sorted(utility.items()):
                        ApproximationValues.append(key)
                        ApproximationDistribution.append(value/utilityNormalization)
                    approximatedValue = numpy.random.choice(ApproximationValues,1, ApproximationDistribution)
                    NoiseDistance = abs(approximatedValue-timestamp)
                else:
                    NoiseDistance = abs(lastrelease-timestamp)
            else:
                NoiseDistance = abs(lastrelease-timestamp)
            MAEDistance.append(NoiseDistance)
            RMSDistance.append(NoiseDistance*NoiseDistance)
            MREDistance.append(NoiseDistance*timestamp)
            budgets.append(0.)
            
        counter += 1
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
