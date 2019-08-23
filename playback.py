# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 19:03:28 2019

@author: Dror
"""

import numpy as np
import simpleaudio as sa
from audio import Audio

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
    
    buffer = np.frombuffer(wav.audio_data, np.int16)
    buffer = np.reshape(buffer,
                        newshape=(wav.num_channels,
                                  int(len(buffer)/wav.num_channels)))#.T.copy(order='C')
    
    audio = Audio(wav.num_channels, wav.sample_rate)
    audio.from_array(buffer)
    
    return audio

def play_Audio(audio, is_wait=False):
    play_obj = sa.play_buffer(audio.audio,
                              num_channels=audio.num_channels,
                              bytes_per_sample=2, # TODO should Audio store this?
                              sample_rate=audio.sample_rate)
    
    if not is_wait:
        input("Type something to quit.")
        play_obj.stop()
    else:
        play_obj.wait_done()











