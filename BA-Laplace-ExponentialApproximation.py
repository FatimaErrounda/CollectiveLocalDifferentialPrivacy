# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 16:15:09 2018

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
    
WindowSize = 70
stepsize = 10
windowepsilon = 1.0

#####
#Budget Absorption
#####

ApproximationsHistory = dict()
ApproximationValues = []
ApproximationDistribution = []
numberofreleases = 0
firststep = 0
secondstep = firststep + WindowSize
distances = []
MAEDistance = []
MREDistance = []
RMSDistance = []
budgets = []
count = 0

while count < len(streamCounts):
    slidingWindow = streamCounts[firststep:secondstep]            
    
    for timestamp in slidingWindow:

        if(count == 0 ):
    #must have a release here to compare to
            lastrelease = slidingWindow[0]
            budgets.append(windowepsilon/(2.0*WindowSize))
            lastreleaseindex = 0
        else:
            distance = timestamp - lastrelease
            distance = abs(distance)
            scale1= (4.0*WindowSize)/windowepsilon
            distance = numpy.random.laplace(distance,scale1)
            to_nullify = ((budgets[lastreleaseindex]*2.0*WindowSize)/windowepsilon) - 1
            if( count - lastreleaseindex <= to_nullify):
                utility = dict()
                if(any(ApproximationsHistory)):
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
                NoiseDistance = abs(approximatedValue-timestamp)
                MAEDistance.append(NoiseDistance)
                MREDistance.append(NoiseDistance*timestamp)
                RMSDistance.append(NoiseDistance*NoiseDistance)
                budgets.append(0.)
            else:
                to_absorb = count - (lastreleaseindex + to_nullify)
                setBudget = (windowepsilon / (2.0*WindowSize))* numpy.minimum(to_absorb, WindowSize)
                scale = 1. / setBudget
                if distance > scale:
                    distances.append(distance)
                    noisycount = numpy.random.laplace(timestamp,scale)
                    NoiseDistance = abs(noisycount-timestamp)
                    MAEDistance.append(NoiseDistance)
                    MREDistance.append(NoiseDistance*timestamp)
                    RMSDistance.append(NoiseDistance*NoiseDistance)
                    lastrelease = noisycount
                    if timestamp in ApproximationsHistory.keys():
                        distanceToApproximation = abs(ApproximationsHistory[timestamp]-timestamp)
                        if( distanceToApproximation > NoiseDistance):
                            ApproximationsHistory[timestamp] = noisycount
                    else:
                        ApproximationsHistory[timestamp] = noisycount
                    lastreleaseindex = count
                    budgets.append(setBudget)
                    numberofreleases += 1
                else:
                    NoiseDistance = abs(approximatedValue-timestamp)
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