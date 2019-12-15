# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 20:57:19 2018

@author: errounda
"""

import json
import numpy

WindowSize = 100
windowepsilon = 1.0
StreamedData = 'appIot_data_24h.json'


print('reading input', StreamedData)

with open(StreamedData, 'r') as f:
    streamCounts = json.load(f)

def StaircaseNoise(epsilon):
    gamma = 1. / (1.+numpy.exp(epsilon*0.5))
    #b = numpy.exp(-epsilon)
    #gamma = (numpy.power(b-(2*b*b)+(2*b*b*b*b)-(b*b*b*b*b), 1./3.) / ((1.-b)*(1.-b)*1.25)) -b/(1.-b)
    b = numpy.exp(-epsilon)
    p0 = gamma / (gamma + (1.-gamma)*b)
    p1 = 1.-p0
    S = numpy.random.choice([-1, 1])
    G = numpy.random.geometric(p=1-b) - 1
    U = numpy.random.uniform(0.0, 1.0)
    B = numpy.random.choice([0, 1], p=[p0, p1])
    X = S * ((1 - B) * ((G + gamma * U) * 1.)+ B * ((G + gamma + (1 - gamma) * U) * 1.))
    return X


budgets = []
count = 0
MAEDistance = []
RMSDistance = []
MREDistance = []
RandomVectorValues = ['0', '1', 'truth']
RRparameter = 1.0 /( numpy.exp(windowepsilon/(2.0*WindowSize)) + 1.0)
RandomVectorProbability =  [RRparameter, RRparameter, 1.0 - 2.0*RRparameter]
numberofreleases = 0
indexSlidingWindow = -1
lastrelease = streamCounts[0]
budgets.append(windowepsilon/WindowSize)
lastreleaseindex = 0
count = 1
firstTime = True
firststep = 1
secondstep = firststep + WindowSize - 1
Threshold = 2

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
        #print('the count=',count,' timestamp=',timestamp)
        distanceToLastRelease = count - lastreleaseindex
        if(abs(timestamp-streamCounts[lastreleaseindex]) >= Threshold):
            #print('the distance is bigger than the threshold ')
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
                    #print('the indexSlidingWindow is', indexSlidingWindow, 'budgetsum is', budgetsum)
                    ramainingBudgetBackward = ((0.5*windowepsilon) - budgetsum)/2.0
                else:
                    ramainingBudgetBackward = timestampbudgetForward
                #print('the ramainingBudgetBackward is', ramainingBudgetBackward)
                timestampbudget = min(timestampbudgetForward, ramainingBudgetBackward)
                #print('the min between ',ramainingBudgetBackward,'and ',timestampbudgetForward,' is', min(timestampbudgetForward, ramainingBudgetBackward))
                #print('the timestampbudget is', timestampbudget)
                scale = 1./timestampbudget
                noisycount = timestamp + StaircaseNoise(timestampbudget)
                NoiseDistance = abs(noisycount-timestamp)
                MAEDistance.append(NoiseDistance)
                MREDistance.append(NoiseDistance*timestamp)
                RMSDistance.append(NoiseDistance*NoiseDistance)
                lastrelease = noisycount
                lastreleaseindex = count
                budgets.append(timestampbudget)
                numberofreleases += 1
            else:
                NoiseDistance = abs(streamCounts[lastreleaseindex]-timestamp)
                if(NoiseDistance>1000):
                    print('the problem is introduced with lastreleaseindex',lastreleaseindex,'timstamp is',timestamp,'streamCounts[lastreleaseindex]', streamCounts[lastreleaseindex])
                MAEDistance.append(NoiseDistance)
                MREDistance.append(NoiseDistance*timestamp)
                RMSDistance.append(NoiseDistance*NoiseDistance)
                budgets.append(0.)
        else:
            #print('skipped release at',  count)
            NoiseDistance = abs(streamCounts[lastreleaseindex]-timestamp)
            MAEDistance.append(NoiseDistance)
            MREDistance.append(NoiseDistance*timestamp)
            RMSDistance.append(NoiseDistance*NoiseDistance)
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
