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

def StaircaseNoise(epsilon):
    gamma = 1. / (1.+numpy.exp(epsilon*0.5))
    b = numpy.exp(-epsilon)
    p0 = gamma / (gamma + (1.-gamma)*b)
    p1 = 1.-p0
    S = numpy.random.choice([-1, 1])
    G = numpy.random.geometric(p=1-b) - 1
    U = numpy.random.uniform(0.0, 1.0)
    B = numpy.random.choice([0, 1], p=[p0, p1])
    X = S * ((1 - B) * ((G + gamma * U) * 1.)+ B * ((G + gamma + (1 - gamma) * U) * 1.))
    return X
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

while (count < len(streamCounts)):

    slidingWindow = streamCounts[firststep:secondstep]        
    if(firststep == 0 ):
    #must have a release here to compare to
        lastrelease = slidingWindow[0]

    count = firststep
    
    for timestamp in slidingWindow:
        #print('count=', count, ' timestamp=',timestamp)
        distance = timestamp - lastrelease
        distance = abs(distance)
        #print('distance=',distance)
        distanceScale = (2.0*WindowSize)/windowepsilon     
        distance = distance+StaircaseNoise(windowepsilon/(2.0*WindowSize))
        if(firststep == 0):
            lowerbound = 0
        else:
            lowerbound = count-WindowSize
        #print('the lowerbound is ', lowerbound,'and the count is ',count)
        budgetsum = numpy.sum(budgets[lowerbound:count])
        #print('the budget is ',budgets[lowerbound:count],'the new sum is', budgetsum)
        remainingBudget = (windowepsilon/2.0) - budgetsum
        scale = 2./remainingBudget
        if distance > scale:
            distances.append(distance)
            noisycount = timestamp+StaircaseNoise(remainingBudget/2.)
            #print('a release is required with budget ',1./scale)
            NoiseDistance = abs(noisycount-timestamp)
            MAEDistance.append(NoiseDistance)
            MREDistance.append(NoiseDistance*timestamp)
            RMSDistance.append(NoiseDistance*NoiseDistance)

            numberofreleases += 1
            lastrelease = noisycount
            budgets.append(remainingBudget/2.)
        else:
            #print('no release is required ')
            NoiseDistance = abs(lastrelease-timestamp)
            MAEDistance.append(NoiseDistance)
            MREDistance.append(NoiseDistance*timestamp)
            RMSDistance.append(NoiseDistance*NoiseDistance)
            budgets.append(0.)
        count += 1
    firststep = secondstep
    secondstep = min(firststep + WindowSize,len(streamCounts))



f.close()