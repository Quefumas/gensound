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


sample_rates = (8000, 11025, 16000, 22050, 24000, 32000, 44100, 48000, 96000)

DB_to_Linear = lambda x: 10**(x/20)
Linear_to_DB = lambda x: 20*np.log(x)/np.log(10)




# converts seconds to samples
# later aliased as a Signal class function
# interprets self.duration as either samples or miliseconds
# i.e. using ints will be affected by sample rate
num_samples = lambda duration, sample_rate: duration \
                                            if isinstance(duration, int) \
                                            else int(duration*sample_rate/sec)
# this is both for readability as well as for
# bottlenecking non-safe conversions from durations into samples,
# for better control later

samples_slice = lambda slc, sample_rate: slice(
                                                None if slc.start is None
                                                     else num_samples(slc.start, sample_rate),
                                                None if slc.stop is None
                                                     else num_samples(slc.stop, sample_rate),
                                                slc.step)


########### 

width_by_coding = {"uint8":1,
                   "int16":2,
                   "int24":3,
                   "int32":4,
                   "float32":4}

def audio_to_bytes(audio, coding="int16"):
    # audio is np.ndarray with dtype flot64
    # strategy is to keep dealing with ndarray w/ multiple channels
    # right until the end, where we shave off bytes and interlace etc.
    assert coding in width_by_coding.keys()
    
    num_channels = audio.shape[0]
    length = audio.shape[1]
    byte_width = width_by_coding[coding]
    
    num_samples = num_channels * length
    total_bytes = num_samples * byte_width
    
    audio = audio.copy(order="C") # leave caller Audio object unaffected
    # Better to write everything 10 times than have a proliferation of
    # partially intersecting subcases
    
    if coding == "uint8": # unsigned
        audio = stretch(audio, byte_width)
        audio += 128
        audio = audio.astype(np.uint8)
        
        buffer = np.zeros(num_samples, dtype=np.uint8)
        
        for i in range(num_channels):
            buffer[i::num_channels] = audio[i]
            
    elif coding == "int16":
        audio = stretch(audio, byte_width)
        audio = audio.astype(np.int16)
        
        buffer = np.zeros(num_samples, dtype=np.int16)
        
        for i in range(num_channels):
            buffer[i::num_channels] = audio[i]
            
    elif coding == "int32": # same treatment as int16
        audio = stretch(audio, byte_width)
        audio = audio.astype(np.int32)
        
        buffer = np.zeros(num_samples, dtype=np.int32)
        
        for i in range(num_channels):
            buffer[i::num_channels] = audio[i]
        
    elif coding == "int24": # no np.int24 so needs manual labor
        audio = stretch(audio, 4) # stretch it to fit 4 bytes, later get rid of LSB
        audio = audio.astype(np.int32)
        
        # TODO superfluous step, merge with the next step sometime
        buffer_temp = np.zeros(num_samples, dtype=np.int32)
        for i in range(num_channels):
            buffer_temp[i::num_channels] = audio[i]
        
        buffer_temp = buffer_temp.tobytes()
        
        buffer = bytearray(total_bytes)
        for i in range(num_samples): # take 3 MSBytes, little endian
            buffer[i*3:i*3+3] = buffer_temp[i*4+1:i*4+4] # TODO this truncates, not rounds
        
    elif coding == "float32": # same byte width as int32 but float, different WAV format
        # don't stretch, leave it in [-1,1]
        audio = audio.astype(np.float32)
        
        buffer = np.zeros(num_samples, dtype=np.float32)
        
        for i in range(num_channels):
            buffer[i::num_channels] = audio[i]
    
    return buffer


def stretch(audio, byte_width):
    """ stretches the samples to cover a range of width 2**bits,
    so we can convert to ints later.
    """
    return audio * (2**(8*byte_width-1) - 1)
    

################

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






















