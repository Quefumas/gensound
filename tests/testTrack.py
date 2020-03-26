# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 23:28:31 2019

@author: Dror
"""

import numpy as np

from Signal import Signal, Sine, Square, Triangle, Sawtooth, GreyNoise, WAV, Step
from transforms import Fade, AmpFreq, Shift, Pan, Extend, \
                       Downsample_rough, Amplitude, \
                       Reverse, Repan, Gain, Limiter, Convolution, Slice, \
                       Mono, ADSR
from filters import Average_samples, LowPassBasic, Butterworth
from curve import Curve, Constant, Line, Logistic, SineCurve, MultiCurve
from playback import play_WAV, play_Audio, export_test # better than export_WAV for debugging

from musicTheory import midC

african = "../data/african_sketches_1.wav"


def curve_continuity_test():
    c = Line(220,330,4e3) | Constant(330, 4e3)
    s = Sine(frequency=c, duration=8e3)
    
    c2 = Constant(220, 2e3) | Line(220, 330, 9e3) | Constant(330, 2e3)
    s = Sine(frequency=c2, duration=18e3)
    audio = s.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, curve_continuity_test)

def to_infinity_curve_test():
    c = Line(-80,-10,10e3)
    p = Line(-100, 100, 5e3)
    #s = Sine(duration=20e3)*Gain(c)
    s = Sine(duration=10e3)*Pan(p)
    audio = s.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, to_infinity_curve_test)

def lowpass_FIR_test():
    #s = WAV(african)[10e3:20e3]*LowPassBasic(cutoff=880, width=100)
    c = Line(55,110, 3e3) | Constant(110,2e3)
    c |= Line(110, 220, 3e3) | Constant(220, 2e3)
    c |= Line(220, 440, 3e3) | Constant(440, 2e3)
    c |= Line(440, 880, 3e3) | Constant(880, 2e3)
    s = Sine(frequency=c, duration=20e3)[0:2]
    s[1] *= LowPassBasic(cutoff=330, width=100)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    # reverse h?
    # using parallel track computation (should be 0.05 the time)
    #export_test(audio, lowpass_FIR_test)

def Butterworth_test():
    s = WAV(african)[10e3:20e3]
    s[1] *= Butterworth(cutoff=880)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, lowpass_FIR_test)

def pan_stereo_test():
    s = WAV(african)[10e3:30e3]
    t = s[0]*Pan(Line(-100,50,20e3)) + s[1]*Pan(Line(0,100,20e3))
    
    # stereo signal panned in space from (-100,0) to (50,100)
    # the stereo field moves right gradually as well as expanding
    # from an opening of 90 degrees to 45 degrees (with headphones)
    Pan.panLaw = -3
    audio = t.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, pan_stereo_test)

def custom_pan_scheme_test():
    '''
    Example of designing a custom panning scheme for multiple channel.
    
    1) Ascertain the topography of the channels in space.
    For our example, consider the following topography:
    
         C
        / \
       /   \
      /     \
     /       \
    L----X----R
    
    We denote the 3 speakers Left, Right and Center.
    These 3 channels will be numbered 0, 1 and 2, respectively.
    The listener is represented as "X".
    
    2) Select an appropriate coordinate system, flexible enough for your purposes.
    We wish to generate a mono signal moving within the triangle above, according
      to some curve yet to be determined.
    There is more than one option for a coordinate system, but we will settle
      on the following:
    
    Any point within the triangle will be represented as a tuple (r, alpha),
      where 0 <= r <= 100 representes the distance from C,
      and -100 <= alpha <= 100 represents the angle (clockwise) from CX
      to the position of the signal.
    
    For example, when r=0, only speaker C will emit a signal.
    When alpha = -100, speaker R will be silent.
    
    Note that the bounds above are rather arbitrary, and so is the
      choice to orient the entire system around speaker C.
    
    3) Create a mapping called a "Gain function" for each speaker, receiving
    a vector and outputting the appropriate Gain level for that speaker.
    
    For simplicity, we will imagine the L-X-R line in our topography to be
      curved in a certain manner, so that the gain in C will only be dependant
      on the r coordinate.
    
    So for C, we wish the gain to range from 0 at r=0 to -infty at r=100.
    For this we employ a variant of the log-shaped pan_shape lambda provided in Pan:
        
        C_pan_shape = lambda x: np.log(x/100)*(-C_panLaw / np.log(2)) + C_compensate
        
    The 100 stretches the values of r from 0 to 100.
    C_compensate allows us to compensate for difference in hardware or distance
      between the speakers.
    C_panLaw is a constant that represents the desired gain at half-way (i.e. r=50).
    This will be elaborated more on later, but for a typical stereo configuration,
      this is often between -3 to -6.
    
    Now, the gain function for C will be:
        CdB = lambda r, alpha: C_pan_shape(100-r) # decreases as r increases
    
    Next, for L/R speakers we start by a traditional stereo configuration,
      which works out of the box using the alpha coordinate, as it ranges
      between -100 and 100, while ignoring r:
    
        LR_pan_shape = lambda x: np.log(x/200 + 0.5)*(-LR_panLaw / np.log(2))
        LdB = lambda r, alpha: pan_shape(-alpha)
        RdB = lambda r, alpha: pan_shape(alpha)
    
    In our topography we assume L/R to be symmetric with respect to the listener,
      and identical in terms of hardware and configuration.
    Thus we define their gain functions symmetrically, and dispense with
      the compensate factor since it is already present in speaker C, and there
      are no other speakers present.
    
    In order to take into account the effects of r, we consider that in the case
      of r=100, the above is fine, and for any other r, we would expect the values
      to be reduced until -infty.
    Thus we add a term to both functions:
        LdB = lambda r, alpha: LR_pan_shape(-alpha) + C_pan_shape(r)
        RdB = lambda r, alpha: LR_pan_shape(alpha) + C_pan_shape(r)
    
    We note that it behaves as required, since Gain is additive.
    
    4) Define the panning scheme, which accepts a location vector as a tuple
    and returns a tuple:
        trianglePanScheme = lambda x: (LdB(*x), RdB(*x), CdB(*x))
    
    5) Define 
    
    '''
    
    ### Panning Scheme setup
    C_panLaw = -6 # these are adjustable parameters
    C_compensate = -5
    LR_panLaw = -3
    
    C_pan_shape = lambda x: np.log(x/100)*(-C_panLaw / np.log(2)) + C_compensate
    CdB = lambda r, alpha: C_pan_shape(100-r)
    
    LR_pan_shape = lambda x: np.log(x/200 + 0.5)*(-LR_panLaw / np.log(2))
    LdB = lambda r, alpha: LR_pan_shape(-alpha) + C_pan_shape(r)
    RdB = lambda r, alpha: LR_pan_shape(alpha) + C_pan_shape(r)
    
    trianglePanScheme = lambda x: (LdB(*x), RdB(*x), CdB(*x))
    
    ### Defining the signal movement in space and time
    step = 3e3 # time to do each arch on the triangle, going L->C->R->L
    
    rCurve = Line(100,0,step) | Line(0,100,step) | Constant(100, step) #try without constant for infinite continuation
    alCurve = Constant(-100, step) | Constant(100, step) | Line(100,-100,step)
    perimeter = MultiCurve(rCurve, alCurve)
    
    ### Generate the signal
    s = Sine(duration=step*3)*Pan(perimeter, scheme=trianglePanScheme)
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    export_test(audio, custom_pan_scheme_test)
    pass

def test_something():
    ...

if __name__ == "__main__":
    Butterworth_test()
    #%%%%%




















