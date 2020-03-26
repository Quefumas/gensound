# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 19:54:57 2020

@author: Dror
"""

import numpy as np
from curve import MultiCurve, Constant, Line


### Panning Scheme setup
C_pan_shape = lambda x: np.log(x/100)*(6 / np.log(2)) - 5
CdB = lambda x: C_pan_shape(100-x[0])

LR_pan_shape = lambda x: np.log(x/200 + 0.5)*(3 / np.log(2))
LdB = lambda x: LR_pan_shape(-x[1]) + C_pan_shape(x[0])
RdB = lambda x: LR_pan_shape(x[1]) + C_pan_shape(x[0])

tPS = lambda x: np.asarray([LdB(x), RdB(x), CdB(x)])
### Defining the signal movement in space and time
step = 3e3 # time to do each arch on the triangle, going L->C->R->L

rCurve = Line(100,0,step) | Line(0,100,step) | Constant(100, step) #try without constant for infinite continuation
alCurve = Constant(-100, step) | Constant(100, step) | Line(100,-100,step)
perimeter = MultiCurve(rCurve, alCurve)



## default scheme
pan_shape = lambda x: np.log(x/200 + 0.5)*(6 / np.log(2))
LdB_ = lambda x: pan_shape(-x)
RdB_ = lambda x: pan_shape(x)
defaultStereo = lambda x: (LdB_(x), RdB_(x))







# pans = perimeter.flatten(3)
pans1 = np.asarray([(0,0),
                    (50,-100),
                    (50,100)], dtype=(np.float64,)*2).T
pans2 = np.asarray([-100,0,100])

#dBs = trianglePanScheme(pans)
dBs = tPS(pans1).T





















