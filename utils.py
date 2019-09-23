# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 18:33:04 2019

@author: Dror

utility functions

"""

import numpy as np


ints_by_width = (np.int8, np.int16, np.int32, np.int64)


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
