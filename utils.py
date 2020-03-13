# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 18:33:04 2019

@author: Dror

utility functions

"""

from numbers import Number
from collections import Callable
import numpy as np


isnumber = lambda x: isinstance(x, Number)
iscallable = lambda x: isinstance(x, Callable)
# TODO there is also the controversial built-in callable()

sec = 1000


ints_by_width = (np.int8, np.int16, np.int32, np.int64)

DB_to_Linear = lambda x: 10**(x/20)
Linear_to_DB = lambda x: 20*np.log(x)/np.log(10)




# converts seconds to samples
# later aliased as a Signal class function
num_samples = lambda duration, sample_rate: int(duration*sample_rate/sec)
# this is both for readability as well as for
# bottlenecking non-safe conversions from durations into samples,
# for better control later

samples_slice = lambda slc, sample_rate: slice(
                                                None if slc.start is None
                                                     else num_samples(slc.start, sample_rate),
                                                None if slc.stop is None
                                                     else num_samples(slc.stop, sample_rate),
                                                slc.step)









def lambda_to_range(f):
    """ transforms function from convenient lambda format to something usable
    for Pan and Amplitude (i.e. shift-sensitive transforms)
    """
    if not iscallable(f):
        f = lambda k: k
    return lambda length, sample_rate: np.asarray([f(x/sample_rate) for x in range(length)], dtype=np.float64)
    # TODO this does not take sample rate into account!


def freq_to_phase(f):
    """ transforms f: time -> frequency to
    g: time -> momentary phase
    """
    # freq being callable
    phase = np.zeros(int(self.sample_rate*self.duration/1000))
    for i in range(1, len(phase)):
        phase[i] = phase[i-1] + 1/self.sample_rate*freq(i/self.sample_rate)
    return 2*np.pi*phase






















