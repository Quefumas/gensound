# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 18:33:04 2019

@author: Dror

utility functions

"""

from numbers import Number
import numpy as np


ints_by_width = (np.int8, np.int16, np.int32, np.int64)
sec = 1000

def lambda_to_range(f):
    """ transforms function from convenient lambda format to something usable
    for Pan and Amplitude (i.e. shift-sensitive transforms)
    """
    if type(f) != type(lambda x:x):
        f = lambda k: k
    return lambda length, sample_rate: np.asarray([f(x/sample_rate) for x in range(length)], dtype=np.float64)
    # TODO this does not take sample rate into account!

DB_to_Linear = lambda x: 10**(x/20)
Linear_to_DB = lambda x: 20*np.log(x)/np.log(10)

is_number = lambda x: isinstance(x, Number)



# converts seconds to samples
# later aliased as a Signal class function
samples = lambda duration, sample_rate: int(duration*sample_rate/sec)
# this is both for readability as well as for
# bottlenecking non-safe conversions from durations into samples,
# for better control later

samples_slice = lambda slc, sample_rate: slice(
                                                None if slc.start is None
                                                     else samples(slc.start, sample_rate),
                                                None if slc.stop is None
                                                     else samples(slc.stop, sample_rate),
                                                slc.step)

















