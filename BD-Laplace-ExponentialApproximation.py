# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 16:13:19 2018

@author: errounda
"""

import json
import numpy



StreamedData = 'appIot_data_24h.json'


print('reading input', StreamedData)

with open(StreamedData, 'r') as f:
    streamCounts = json.load(f)

WindowSize = 100
windowepsilon = 1.0

#####
#Budget Distribution
#####

numberofreleases = 0 
firststep = 0
secondstep = firststep + WindowSize
distances = []
budgets = []
MAEDistance = []
MREDistance = []
RMSDistance = []
count = 0
numberofWindows = 0
ApproximationsHistory = dict()
ApproximationValues = []
ApproximationDistribution = []

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
        distance = numpy.random.laplace(distance,2.0*WindowSize/(windowepsilon))
        utility = dict()
        if(any(ApproximationsHistory)):
            for key, value in ApproximationsHistory.items():
                for key, value in ApproximationsHistory.items():
                    if(value < timestamp + distance and value > timestamp - distance):
                        utility[value] = numpy.exp((windowepsilon*abs(value-timestamp))/(8.0*WindowSize) )
            if(any(utility)):
                utilityNormalization = sum(utility.values())
                for key, value in sorted(utility.items()):
                    ApproximationValues.append(key)
                    ApproximationDistribution.append(value/utilityNormalization)
                approximatedValue = numpy.random.choice(ApproximationValues,1, ApproximationDistribution)
            else:
                approximatedValue = lastrelease
        else:
            approximatedValue = lastrelease
        if(firststep == 0):
            lowerbound = 0
        else:
            lowerbound = count-WindowSize
        budgetsum = numpy.sum(budgets[lowerbound:count])
        remainingBudget = (windowepsilon/2.0) - budgetsum
        scale = 2./remainingBudget
        if distance > scale:
            distances.append(distance)
            noisycount = numpy.random.laplace(timestamp,scale)
            NoiseDistance = abs(noisycount-timestamp)
            MAEDistance.append(NoiseDistance)
            MREDistance.append(NoiseDistance*timestamp)
            RMSDistance.append(NoiseDistance*NoiseDistance)
            if timestamp in ApproximationsHistory.keys():
                distanceToApproximation = abs(ApproximationsHistory[timestamp]-timestamp)
                if( distanceToApproximation > NoiseDistance):
                    ApproximationsHistory[timestamp] = noisycount
            else:
                ApproximationsHistory[timestamp] = noisycount
            numberofreleases += 1
            lastrelease = noisycount

            budgets.append(remainingBudget/2.)

        else:
            #print('no release is required ')
            NoiseDistance = abs(approximatedValue-timestamp)
            MAEDistance.append(NoiseDistance)
            MREDistance.append(NoiseDistance*timestamp)
            RMSDistance.append(NoiseDistance*NoiseDistance)
            #published.append(timestamp)
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