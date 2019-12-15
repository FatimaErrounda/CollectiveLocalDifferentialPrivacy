# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 16:15:09 2018

@author: errounda
"""

import json
import numpy


StreamedData = 'appIot_data_24h.json'

WindowSize = 10
windowepsilon = 30.0

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
#Budget Absorption
#####
firststep = 0
secondstep = firststep + WindowSize
published = []
distances = []
MAEDistance = []
MREDistance = []
RMSDistance = []
budgets = []
count = 0
while count < len(streamCounts):
    slidingWindow = streamCounts[firststep:secondstep]            
    
    for timestamp in slidingWindow:
        #print('count=', count, ' timestamp=',timestamp)
        if(count == 0 ):
    #must have a release here to compare to
            lastrelease = slidingWindow[0]
            published.append(lastrelease)
            budgets.append(windowepsilon/(2.0*WindowSize))
            lastreleaseindex = 0
        else:
            distance = timestamp - lastrelease
            distance = abs(distance)
            #print('distance=',distance)
            scale1= (2.0*WindowSize)/windowepsilon

            distance = distance+StaircaseNoise(windowepsilon/(2.0*WindowSize))
            #print('the noisy distance is ',distance)
            to_nullify = ((budgets[lastreleaseindex]*2.0*WindowSize)/windowepsilon) - 1
            #print('budgets[lastreleaseindex] = ',budgets[lastreleaseindex],'the number of timestamps to nullify ',to_nullify, 'the last release index is ', lastreleaseindex)
            if( count - lastreleaseindex <= to_nullify):
                #print('release is nullified')
                NoiseDistance = abs(lastrelease-timestamp)
                MAEDistance.append(NoiseDistance)
                RMSDistance.append(NoiseDistance*NoiseDistance)
                MREDistance.append(NoiseDistance*timestamp)
                published.append(timestamp)
                budgets.append(0.)
            else:
                #print('release is considered')
                to_absorb = count - (lastreleaseindex + to_nullify)
                #print('the budget to absorb is ',to_absorb)
                setBudget = (windowepsilon / (2.0*WindowSize))* numpy.minimum(to_absorb, WindowSize)
                scale = 1. / setBudget
                if distance > scale:
                    distances.append(distance)
                    noisycount = timestamp +StaircaseNoise(setBudget)
                    NoiseDistance = abs(noisycount-timestamp)
                    MAEDistance.append(NoiseDistance)
                    RMSDistance.append(NoiseDistance*NoiseDistance)
                    MREDistance.append(NoiseDistance*timestamp)
                    lastrelease = noisycount
                    lastreleaseindex = count
                    published.append(noisycount)
                    budgets.append(setBudget)
                else:
                    NoiseDistance = abs(lastrelease-timestamp)
                    MAEDistance.append(NoiseDistance)
                    RMSDistance.append(NoiseDistance*NoiseDistance)
                    MREDistance.append(NoiseDistance*timestamp)
                    published.append(timestamp)
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