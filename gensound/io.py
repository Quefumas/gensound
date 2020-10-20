# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 19:03:28 2019

@author: Dror

This file contains the entire interface of the library with the OS.
This includes reading and writing files, and real-time playback.

All of these functionalities should be enclosed in this file,
so as to facilitate cross-platform functionality in the future.

This supports the following basic functionalities:
    * playback from Audio instance
    * Audio instance to file (whatever format possible)
    * file to Audio instance

There is a class for each supported I/O library, which provides these functions
for that library in particular. When this file is loaded, the desired libraries
are determined from settings.py (TODO).

"""

import wave
import inspect
import time

import numpy as np
import simpleaudio as sa
from gensound.settings import _supported

# we start with the support for the various libraries,
# put the exported functionality down below

class _IO_wave:
    is_supported = True # python built-in
    
    @staticmethod
    def export_WAV(filename, audio):
        file = wave.open(filename, "wb")
        file.setnchannels(audio.num_channels)
        file.setsampwidth(audio.byte_width)
        file.setframerate(audio.sample_rate)
        file.setnframes(audio.length)
    
        file.writeframes(audio.buffer)

class _IO_SA:
    is_supported = "simpleaudio" in _supported
    
    @staticmethod
    def playback(audio, is_wait=True): # plays Audio instance
        #audio.buffer = audio.buffer.copy(order='C')
        play_obj = sa.play_buffer(audio.buffer,
                                  num_channels=audio.num_channels,
                                  bytes_per_sample=audio.byte_width, # TODO should Audio store this?
                                  sample_rate=audio.sample_rate)
        
        if not is_wait or audio.audio.shape[1] > 3*10**5:
            input("Type something to quit.")
            play_obj.stop()
        else:
            play_obj.wait_done()


def export_test(audio, func=None):
    assert inspect.stack()[1].function == func.__name__, "logging names don't match!!!"
    
    timestamp = time.strftime('%Y-%b-%d_%H%M', time.localtime())
    export_WAV("../output/export_{timestamp}_{caller.function}.wav".format( 
                   timestamp = timestamp,
                   caller = inspect.stack()[1]),
                audio)
    
    if func is None:
        return
    
    with open("../output/_export_log.txt", "a") as file:
        # TODO make sure not to overwrite
        file.write("++++++ {} ++++++\n------ {} ------\n\n{}\n\n".format(
                                                               func.__name__,
                                                               timestamp,
                                                               inspect.getsource(func)))

def play_WAV(filename="", is_wait=False):
    wav = sa.WaveObject.from_wave_file(filename)
    play = wav.play()
    
    if not is_wait:
        input("Type something to quit.")
        play.stop()
    else:
        play.wait_done()


def WAV_to_Audio(filename=""):
    wav = sa.WaveObject.from_wave_file(filename)
    # TODO type np.int16
    buffer = np.frombuffer(wav.audio_data, np.int16).astype(np.float64)
    
    buffer = np.reshape(buffer,
                        newshape=(wav.num_channels,
                                  int(len(buffer)/wav.num_channels))[::-1]).T.copy(order='C')
    buffer /= 2**(8*wav.bytes_per_sample-1)
    # TODO the above needs some consideration
    # should we convert to float immediately, or wait till the last minute?
    # is this the right place to convert?
    # and should this be normalized in some way in relation to the synthesized signals?
    from gensound.audio import Audio
    audio = Audio(wav.sample_rate)
    audio.from_array(buffer)
    
    return audio



###################
'''
Here are the exported functionalities.
TODO add logic to figure out supported libraries (also let user customize),
and direct traffic to the correct classes.
also figure out how to navigate different formats
'''

export_WAV = _IO_wave.export_WAV
play_Audio = _IO_SA.playback # should be named 'playback' anywhere but in Audio









