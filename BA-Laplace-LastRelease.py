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


#####
#Budget Absorption
#####
firststep = 0
secondstep = firststep + WindowSize
MAEDistance = []
MREDistance = []
RMSDistance = []
budgets = []
count = 0

while count < len(streamCounts):
    slidingWindow = streamCounts[firststep:secondstep]              
    for timestamp in slidingWindow:
        if(count == 0 ):
            lastrelease = slidingWindow[0]
            budgets.append(windowepsilon/(2.0*WindowSize))
            lastreleaseindex = 0
        else:
            distance = timestamp - lastrelease
            distance = abs(distance)
            scale1= (2.0*WindowSize)/windowepsilon
            distance = numpy.random.laplace(distance,scale1)
            to_nullify = ((budgets[lastreleaseindex]*2.0*WindowSize)/windowepsilon) - 1
            if( count - lastreleaseindex <= to_nullify):
                #print('release is nullified')
                NoiseDistance = abs(lastrelease-timestamp)
                MAEDistance.append(NoiseDistance)
                MREDistance.append(NoiseDistance*timestamp)
                RMSDistance.append(NoiseDistance*NoiseDistance)
                budgets.append(0.)
            else:
                to_absorb = count - (lastreleaseindex + to_nullify)
                setBudget = (windowepsilon / (2.0*WindowSize))* numpy.minimum(to_absorb, WindowSize)
                scale = 1. / setBudget
                if distance > scale:
                    noisycount = numpy.random.laplace(timestamp,scale)
                    NoiseDistance = abs(noisycount-timestamp)
                    MAEDistance.append(NoiseDistance)
                    RMSDistance.append(NoiseDistance*NoiseDistance)
                    MREDistance.append(NoiseDistance*timestamp)
                    lastrelease = noisycount
                    lastreleaseindex = count
                    budgets.append(setBudget)
                else:
                    NoiseDistance = abs(lastrelease-timestamp)
                    MAEDistance.append(NoiseDistance)
                    RMSDistance.append(NoiseDistance*NoiseDistance)
                    MREDistance.append(NoiseDistance*timestamp)
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