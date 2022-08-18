# -*- coding: utf-8 -*-
"""
Outdated but detailed example of custom panning schemes for multiple speakers.
"""

import numpy as np

from Signal import Signal, Sine, Square, Triangle, WAV
from transforms import Fade, Shift, Pan, Extend, Repan, Gain
from filters import LowPassBasic, Butterworth
from curve import Curve, Constant, Line, Logistic, SineCurve, MultiCurve
from playback import play_WAV, play_Audio, export_test # better than export_WAV for debugging


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
      where 0 <= r <= 100 represents the distance from C,
      and -100 <= alpha <= 100 represents the angle (clockwise) from CX
      to the position of the signal.
    
    For example, when r=0, only speaker C will emit a signal.
    When alpha = -100, speaker R will be silent.
    
    Note that the bounds above are rather arbitrary, and so is the
      choice to orient the entire system around speaker C.
    
    3) Create a mapping called a "Gain function" for each speaker, receiving
    a vector and outputting the appropriate Gain level for that speaker.
    
    For simplicity, we will imagine the L-X-R line in our topography to be
      curved in a certain manner, so that the gain in C will only be dependent
      on the r coordinate.
    
    So for C, we wish the gain to range from 0 at r=0 to -infty at r=100.
    For this we employ a variant of the log-shaped pan_shape lambda provided in Pan:
        
        C_pan_shape = lambda x: np.log(x/100)*(-C_panLaw / np.log(2))
        
    The 100 stretches the values of r from 0 to 100.
    C_panLaw is a constant that represents the desired gain at half-way (i.e. r=50).
    This will be elaborated more on later, but for a typical stereo configuration,
      this is often between -3 to -6.
    
    Now, the gain function for C will be:
        CdB = lambda r, alpha: C_pan_shape(100-r) + C_compensate # decreases as r increases
    C_compensate allows us to compensate for difference in hardware or distance
      between the speakers, see later on.
    
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
    
    5) Define a MultiCurve that governs the behavior of all coordinates
    across time.
        step = 3e3
        rCurve = Line(100,0,step) | Line(0,100,step) | Constant(100, step)
        alCurve = Constant(-100, step) | Constant(100, step) | Line(100,-100,step)
        perimeter = MultiCurve(rCurve, alCurve)
    
    A MultiCurve is simply two or more curves strung together, each representing
      a different coordinate of the signal position vector. "rCurve" represents
      the change in the r coordinate, and "alCurve" represents the change in
      the alpha coordinate.
    We combine them together to form a "perimeter" MultiCurve, which traces
      the signal going from L to C to R and back to L, taking 3 seconds for
      each leg of the journey.
    
    6) Apply the panning and indicate the custom panning scheme defined:
        s = SomeSignal*Pan(perimeter, scheme=trianglePanScheme)
    
    7) Now we can mixdown and play or export the track in the normal fashion,
    but keep in mind that not all playback interfaces are capable of handling
    more than 2 channels, and some of them may require additional configurations
    to enable it. The 3rd channel is often taken by default to be a "mono"
    channel, and there are other similar behaviors which are sometimes default
    for certain players and channels.
    Depending on the software and hardware setup, it may be easier to export
      each channel separately.
    
    8) Finally, we should perform experiments in the playback environment, and
    fine-tune the gain parameters accordingly. In our case, the LR_panLaw parameter
    acts exactly to the usual pan law, so it is easier to solve. But we should
    also use our ears and adjust the values for C_panLaw, which governs the
    panning away and from speaker C. C_compensate may be used to give a constant
    boost or decrease in gain for C, to compensate for difference in hardware
    and distance from the listener.
    However, gain compensation for various speakers may also be easily applied
      by applying Gain() to the individual channels, pre-mixdown, or by adjusting
      the levels on the hardware on the spot.
    
    There are no hard and fast rules for this; you must experiment and listen.
    Also, remember that we cheated slightly in our definition of the topography:
      we treated the line L-X-R as curved, while in reality it is not, so
      theoretically this could cause speaker C to be too high in gain when the
      signal is located in the center field.
    In this toy example this is probably not a big issue, but these details
      should be kept in mind as well.
    
    '''
    
    ### Panning Scheme setup
    C_panLaw = -6 # these are adjustable parameters
    C_compensate = -5
    LR_panLaw = -3
    
    C_pan_shape = lambda x: np.log(x/100)*(-C_panLaw / np.log(2))
    CdB = lambda r, alpha: C_pan_shape(100-r) + C_compensate
    
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
    
