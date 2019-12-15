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
    
WindowSize =100
windowepsilon = 1.0

count = len(streamCounts)

MAEDistance = []
RMSDistance = []
MREDistance= []
for timestamp in streamCounts:

    scale = 1./(windowepsilon/WindowSize)
    noisycount = numpy.random.laplace(timestamp,scale)
    NoiseDistance = abs(noisycount-timestamp)
    MAEDistance.append(NoiseDistance)
    MREDistance.append(NoiseDistance*timestamp)
    RMSDistance.append(NoiseDistance*NoiseDistance) 
     
MAEValue = numpy.sum(MAEDistance)/count
MREValue = numpy.sum(MREDistance)/count
RMSEValue = numpy.sqrt(numpy.sum(RMSDistance)/count)
print('the MAE is ',MAEValue)
print('the RMS is ', MREValue)
print('the RMS is ', RMSEValue)

f.close()
