# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 11:56:08 2020

@author: Dror
"""

from timeit import timeit

def test_timeit():
    setup = '''
import numpy as np
a = np.ones((2,1000), dtype=np.float64)
'''
    
    print(timeit(setup=setup, stmt="b=5*a", number=1000))

def test_convolution():
    #setup = "import numpy as np; a=np.ones(("
    setup = '''
import numpy as np
x = 100
n = 10000
h = np.linspace(start=1, stop=10, num=x)
audio = np.ones((2,n), dtype=np.float64)
''' 
    stmt1 = '''
padded = np.pad(audio, ((0,0),(len(h)-1,0)))
res = np.zeros_like(audio, dtype=np.float64)

for i in range(audio.shape[1]):
    res[:,i] = np.sum(h*padded[:,i:i+len(h)], axis=1)
'''

    # here h is assumed to be reversed as well
    stmt2 = '''
parallel = np.zeros((len(h), audio.shape[0], audio.shape[1]+len(h)-1), dtype=np.float64)
for i in range(len(h)):
    parallel[i,:,i:n+i] = h[i]*audio
res = np.sum(parallel, axis=0)[:,:n]
'''

    # here h is assumed to be reversed as well
    stmt2_2 = '''
padded = np.pad(audio, ((0,0),(len(h)-1,0)))
res = np.zeros_like(audio, dtype=np.float64)
for i in range(len(h)-1):
    res += h[i]*padded[:,i:audio.shape[1]+i]
'''
    
    
    # here the result is different because h was reversed before
    stmt3 = '''
res=np.asarray([np.convolve(h, audio[0,:], mode='full'), np.convolve(h,audio[1,:], mode='full')])[:,:n]
'''
    stmt4 = '''
res=np.asarray([np.convolve(h, audio[0,:], mode='same'), np.convolve(h,audio[1,:], mode='same')])
'''

    num = 100
    print("repeated multiplication: {}".format(timeit(setup=setup, stmt=stmt1, number=num)))
    print("summing parallel tracks: {}".format(timeit(setup=setup, stmt=stmt2, number=num)))
    print("cumulative sum: {}".format(timeit(setup=setup, stmt=stmt2_2, number=num)))
    print("using np.convolve (mode='full'): {}".format(timeit(setup=setup, stmt=stmt3, number=num)))
    print("using np.convolve (mode='same'): {}".format(timeit(setup=setup, stmt=stmt4, number=num)))

if __name__ == "__main__":
    test_convolution()
    # TODO google convolution in np


















