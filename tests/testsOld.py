# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 15:04:25 2019

@author: Dror



This file is to store old test functions, for reference and to document
them later as examples.
"""

import numpy as np

from Signal import Signal, Sine, Square, Triangle, Sawtooth, GreyNoise, WAV, Step
from transforms import Fade, AmpFreq, Shift, Pan, Extend, \
                       Downsample_rough, Amplitude, \
                       Reverse, Repan, Gain, Limiter, Convolution, Slice, \
                       Mono, ADSR
from filters import Average_samples
from curve import Curve, Constant, Line, Logistic, SineCurve, MultiCurve
from playback import play_Audio, export_test

from musicTheory import midC

african = "../data/african_sketches_1.wav"

def melody_test():
    step = 500
    notes = (midC(0), midC(-3), midC(-7), midC(4), midC(7), midC(-1), midC(2))
    t = sum([Sine(frequency=f, duration=step+100)*
             Fade(is_in=True, duration=step*5)*
             Fade(is_in=False, duration=step+100)*
             Shift(duration=(1+i)*step)
             for (i,f) in enumerate(notes)])
    audio = t.mixdown(sample_rate=11025, byte_width=2)
    play_Audio(audio)

def only_signal_harmonics(f=220, seconds=10):
    params = [(0.34, 1, 2, 0.45),
              (0.2, 1.94, 3, 0.7),
              (0.2, 3, 2.3, 0.3),
              (0.15, 3.9994, 2.1, 0.67),
              (0.19, 5.1, 0.8, 0.46),
              (0.12, 5.96, 1.3, 0.34),
              (1/7, 7, 1.2, 0.5),
              (0.119, 8.1, 2.9, 0.23),
              (0.2, 9, 1.3, 0.4),
              (1/10, 9.87, 0.65, 0.4),
              ]
    
    t = sum([p[0]*Triangle(frequency=f*p[1], duration=seconds*1000)*\
             AmpFreq(frequency=p[2], size=p[3])*\
             Fade(is_in=True, duration=3)*\
             Shift(duration=1*1000) for p in params])
    audio = t.mixdown(sample_rate=11025, byte_width=2)
    play_Audio(audio)

def simple_test(f=220, seconds=5):
    t = 0.7*Sine(frequency=230, duration=seconds*1000)*AmpFreq(frequency=1, size=0.2)[0:2]
    t[1] += Triangle(frequency=380, duration=seconds*1000)*AmpFreq(frequency=0.4, size=0.3)
    t[0] += Square(frequency=300, duration=seconds*1000)*AmpFreq(frequency=0.7, size=0.2)
    t *= Fade(is_in=True, duration=3*1000)
    #t *= Fade(is_in=False, duration=20)
    t *= Shift(duration=1*1000)
    play_Audio(t.mixdown())

def WAV_test(filename=""):
    wav = WAV(filename)
    wav *= AmpFreq(frequency=0.06, size=0.3)
    wav *= Fade(is_in=True, duration=10)
    
    wav += 0.03*GreyNoise(duration=20*1000)*AmpFreq(frequency=0.03, size=0.2)
    wav += (0.06*0.7)*Triangle(frequency=230, duration=30)*Fade(is_in=True, duration=3*1000)[0:2]
    
    audio = wav.mixdown(sample_rate=44100, byte_width=2)
    
    #play_Audio(ad, is_wait=True)
    
    
def timing_test():
    t = 0.7*Sine(frequency=230, duration=3*1000)*AmpFreq(frequency=1, size=0.2)[0:2]
    t += Square(frequency=250, duration=3*1000)*Shift(duration=3*1000)
    audio = t.mixdown(sample_rate=11025, byte_width=2)
    play_Audio(audio, is_wait=True)


def pan_test():
    seconds = 10
    t = Sine(frequency=230, duration=seconds*1000)[0:2]#*AmpFreq(frequency=1, size=0.2)
    
    top = seconds*11025
    
    pans = (lambda x: np.log(1+(np.e-1)*(top-x)/top),
            lambda x: np.log(1+(np.e-1)*x/top))
    
    
    #t *= Pan(*pans) # not relevant for new Pan
    
    audio = t.mixdown(sample_rate=11025, byte_width=2)
    play_Audio(audio, is_wait=True)


def step_test():
    times = (1, 3)
    
    t = sum([Step()*Shift(duration=time*1000) for time in times])*Extend(1000)
    #t = Step(1)
    audio = t.mixdown(sample_rate=11025, byte_width=2)
    play_Audio(audio)

def downsample_test(filename):
    wav = WAV(filename)
    wav *= Downsample_rough(factor=5, phase=0)
    audio = wav.mixdown(sample_rate=44100, byte_width=2)
    
    play_Audio(audio, is_wait=True)


def averagesample_test(filename):
    wav = WAV(filename)
    #wav *= Average_samples(5,4,3,2,1,2,3,4,5)
    wav *= Average_samples(1,1,1,1,1,1,1,1,1)
    #wav *= Average_samples(25,16,9,4,1,4,9,16,25)
    #wav *= Average_samples(1,0,0,0,0,0,0,0,1)
    #wav *= Average_samples(1,-1,1,-1,1,-1,1,-1,1)
    #wav *= Average_samples(-1,-1,-1,-1,10,-1,-1,-1,-1) # high pass!
    audio = wav.mixdown(sample_rate=44100, byte_width=2)
    
    play_Audio(audio, is_wait=True)

def dummy_reverb_test():
    #amp = lambda x: 
    #wav = WAV(african) + WAV(african)*Amplitude(amp)*Shift(duration=500)
    #wav = WAV(african)*AmpFreq(frequency=0.12, size=0.25)
    #wav += WAV(african)*AmpFreq(frequency=0.12, size=0.25, phase=np.pi)*Shift(duration=500)*Average_samples(1,1,1,1,1,1,1,1,1)
    
    wav = sum([(1-8/10)*WAV(african)*Shift(duration=100*x)*Average_samples(2*x+1) for x in range(5)])
    wav += 0.6*WAV(african)*Downsample_rough(factor=5)*Average_samples(5)
    
    audio = wav.mixdown(sample_rate=44100, byte_width=2)
    play_Audio(audio, is_wait=True)
    #filename="data/african_plus_reverb_with_added_lowpass_downsample.wav"

def repan_reverb_test():
    # TODO these aren't relevant for new pan
    wav = sum([(1-8/10)*WAV(african)*Shift(duration=100*x)*Average_samples(2*x+1)*Pan(*(1,0.3)[::(1 if x%2==0 else -1)]) for x in range(5)])
    wav += 0.6*WAV(african)*Pan(0,None)*Downsample_rough(factor=5)*Average_samples(5)
    wav += 0.6*WAV(african)*Pan(None,1)
    
    audio = wav.mixdown(sample_rate=44100, byte_width=2)
    play_Audio(audio, is_wait=True)

def reverse_test():
    wav = WAV(african)*Reverse()*Downsample_rough(factor=5)*Average_samples(5)
    wav += WAV(african)*Shift(duration=150)*Average_samples(1,1,1,1,1,1,1,1,1)
    
    audio = wav.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.09)
    play_Audio(audio, is_wait=True)
    


def t1():
    t = Triangle(frequency=midC(-1.5), duration=5000)*Average_samples(21)*AmpFreq(frequency=0.8, size=0.3)
    
    env = lambda n: (n/1000) if n < 1000 else (0.5+np.sin(2*np.pi*2*n/1000)/2)
    env = lambda n: (0.5+np.sin(2*np.pi*2*n)/2)
    env = lambda n: (0 if n == 0 else np.sin(n)*(min(n, 1)))
    env = lambda n: np.e**(-0.3+0.3*(min(n,0.3))/0.3)
    t += 0.01*Sawtooth(frequency=midC(-1.5), duration=5000)*Amplitude(env)
    
    audio = t.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.01)
    play_Audio(audio)
    

def envelope_test():
    env = lambda n: (n/1000) if n < 1000 else (0.5+np.sin(2*np.pi*2*n/1000)/2)
    env = lambda n: (0.5+np.sin(2*np.pi*2*n)/2)
    env = lambda n: (0 if n == 0 else np.sin(n)*(min(n, 1)))
    env = lambda n: np.e**(-3+3*(min(n,3))/3)
    wav = Sine(duration=5000)*Amplitude(env)
    
    audio = wav.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.03)
    play_Audio(audio, is_wait=True)

def reuse_WAV_test():
    wav = WAV(african)
    signal = wav*Reverse() + wav*Shift(duration=150)
    print(signal)
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.09)
    play_Audio(audio, is_wait=True)

def repan_test():
    signal = WAV(african)*Repan(1,0) #switch L/R
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=None)
    play_Audio(audio, is_wait=True)
    pass

def log_amp_test():
    # tests logarithmic scaling of amplitude factors
    signal = WAV(african)*Repan(0,None) #switch L/R
    signal += 0.125*WAV(african)*Repan(None,1)
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.5)
    play_Audio(audio, is_wait=True)
    pass

def gain_test():
    signal = WAV(african)*Repan(0,None)
    signal += WAV(african)*Repan(None,1)*Gain(-9)
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=None)
    play_Audio(audio, is_wait=True)

def limit_test():
    signal = WAV(african)
    signal *= Limiter(max_amplitude=0.1)
    #signal *= Limiter(max_ratio=0.9)
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.9)
    play_Audio(audio, is_wait=True)

def cancellation_test():
    #signal = Sine(duration=5000) - 0.999*Sine(duration=5000)
    #signal += 0.01*Sine(frequency=130,duration=1000)
    signal = WAV(african) - WAV(african)*Repan(1,0)
    #signal += 0.5*WAV(african) # basically neautralized the center "channel"
    #signal += 5.0*WAV(african) # strengthens center
    
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio, is_wait=True)

def nonmatching_samplings():
    signal = WAV(african) # its the users responsibility to know the sample rates
    audio = signal.mixdown(sample_rate=32000, byte_width=2, max_amplitude=0.2)
    # 8k, 11025, 16k, 22050, 24k, 32k, 44.1k, 48k, 88.2k, 96k, 192k
    play_Audio(audio, is_wait=True)

def convolution_test():
    signal = WAV(african)*Convolution(forward=False, add=0.3, is_both_ways=False)*Average_samples(11)
    signal -= 0.1*WAV(african)
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio, is_wait=True)

def after_test_1():
    signal = Sine(frequency=midC(-7), duration=6e3)
    s2 = Signal.concat(*[Sine(frequency=midC(k-4), duration=1e3) for k in range(6)])
    signal += s2
    
    print(signal)
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio, is_wait=True)

def after_test_2():
    # test ** as repeat
    s = Signal.concat(Sine(midC(-7+12), 1e3), Sine(midC(-3), 1e3), Sine(midC(-8+12), 1e3), Sine(midC(-1), 1e3))
    s **= 5
    s += WAV(african)
    
    print(s)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio, is_wait=True)

def after_test_3():
    b1 = 1.2e3
    b2 = 1e3
    b3 = 0.8e3
    b4 = 1.4e3
    
    p1 = [-6, -3, -8, -1, 1]
    p2 = [9, 4, 6, 8, 11]
    p3 = [12+1, 12+4, 12+6, 12+8, 12+1, 12+3, 12+11]
    p4 = [-12+2, -12-1, -12+1, -12-3]
    
    s = Signal.concat(*[Sine(midC(p), b1) for p in p1])**5
    s += 0.8*Signal.concat(*[Sine(midC(p), b2) for p in p2])**6*Shift(000)
    s += 0.3*Signal.concat(*[Sine(midC(p), b3) for p in p3])**6
    s += 2*Signal.concat(*[Sine(midC(p), b4) for p in p4])**5
    s *= Average_samples(11)
    
    print(s)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio, is_wait=False)
    #"data/sine loops 4 voices.wav"

def solfege_test_1():
    num_notes = 20
    duration = 0.5e3
    silence = 0.5e3
    starting_note = 0
    Note = Triangle
    
    notes = [Note(starting_note, duration)*Extend(silence)]
    for i in range(num_notes):
        starting_note += np.random.randint(-4, 5)
        notes.append(Note(midC(starting_note), duration)*Extend(silence))
    
    s = Signal.concat(*notes)
    audio = s.mixdown(sample_rate=22050, byte_width=2, max_amplitude=0.2)
    play_Audio(audio, is_wait=False)

def db_fade_test():
    #signal = Sine(duration=4e3)*Fade(is_in=True, duration=1000)
    signal = WAV(african)*Fade(is_in=True, duration=2e3)
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio, is_wait=True)


###################################
    
    
def slice_test():
    hihat = WAV(african)[:1061]*Average_samples(5)
    hihat **= 30
    
    part = WAV(african)[5*1061:5*1061+3*1061]
    part**=20
    s = WAV(african) + part*Shift(4*1061)*Gain(-6) - hihat
    #s = hihat
    audio = s.mixdown(sample_rate=32000, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, slice_test)

def slice_set_test():
    s = WAV(african)
    # careful with 5e3, creates float slices
    
    #s[5e3:18e3] = s[5e3:18e3]*Repan() + s[5e3:18e3]*Downsample_rough(5)*Gain(-3)
    #s[5e3:18e3] *= Repan(1,0)
    s[5e3:18e3] = s[5e3:18e3]*Repan(1 ,None) + s[5e3:18e3]*Repan(None, 0)
    # TODO found a bug here? does it really keep both copies of the slice separate?
    # also test s = s[0:50] & sine() & s[50:100]
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, slice_set_test)

def concat_overload_test():
    #s = Sine(frequency=250, duration=2e3) | Triangle(frequency=300, duration=3e3)
    s = WAV(african)
    
    s = s[5e3:5.5e3] | s[6e3:6.8e3] | s[11e3:13e3]*Reverse()+Sine(frequency=300, duration=2e3) | s[9e3:10.8e3]
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, concat_overload_test)

def messy_random_concat_test():
    s = WAV(african)
    
    max_length = 20e3
    
    def messy_track():
        t = 0
        temp = 0
        
        while temp < max_length:
            duration = 400 + np.random.random()*3e3
            temp += duration
            start = 4e3 + (30-4)*np.random.random()*1e3
            t |= s[start:start+duration]
        
        return t
    
    
    L = messy_track() + messy_track()
    R = messy_track() + messy_track()
    
    s = L*Repan(0, None) + R*Repan(None, 1)
    
    t = sum([(1-8/10)*s*Shift(duration=100*x)*Average_samples(weights=2*x+1) for x in range(5)])
    t += 0.6*s*Downsample_rough(factor=5)*Average_samples(weights=5)
    
    audio = t.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, messy_random_concat_test)
    
def concat_scalar_test():
    s = WAV(african)
    
    gap = 0.03
    L = s[10e3:11e3] | gap | s[11e3:12e3] | gap | s[12e3:13e3] | gap | s[13e3:14e3] \
        | gap | s[14e3:15e3] | gap | s[15e3:16e3] | gap | s[16e3:24e3]
    R = s[10e3:18e3] | gap | s[18e3:19e3] | gap | s[19e3:20e3] | gap | s[20e3:21e3] \
        | gap | s[21e3:24e3]
    
    s = L*Repan(0, None) + R*Repan(None, 1)
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, concat_scalar_test)
    # this is a funky effect of panning by dephasing...

def reverse_phase_test():
    s = WAV(african)
    
    L = s[10e3:11e3] | -s[11e3:12e3] | s[12e3:13e3] | -s[13e3:14e3] | s[14e3:15e3] \
        | -s[15e3:16e3] | s[16e3:17e3]
    R = s[10e3:17e3]
    
    s = L*Repan(0, None) + R*Repan(None, 1)
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, reverse_phase_test)

def channel_slice_test():
    # series of tests
    #s = WAV(african)[5e3:15e3]
    
    # t = s[0]
    # t = s[1,1e3:7e3]
    # t = s[1e3:7e3]
    
    #s[1] = 0.132*GreyNoise(duration=10e3)#*Gain(-20)
    
    #s[0,3e3:7e3] = s[1,2e3:6e3]
    #s[0,1e3:6e3] += 0.13*Sine(frequency=midC(8))
    #s[0,1e3:5e3] *= Reverse()
    #s[1] = s[0]*Gain(-6)
    # etc...
    
    ##########
    s = 0.1*Sine()
    s[1] = WAV(african)[0,5e3:15e3]
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, channel_slice_test)

def test_gain_dB():
    s = Signal()
    
    for i in range(10):
        s |= Sine(duration=1e3)*Gain(-6*i)
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)

def test_filter_noise():
    g = GreyNoise()
    g *= Average_samples(0.04, 0.12, 0.2, 0.12, 0.04)
    #g *= Average_samples(5)
    audio = g.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)




def test_reverse_channels():
    s = WAV(african)[15e3:25e3]
    s[0] += (WAV(african)[15e3:35e3:2]*Gain(-6))[1]
    s[1] += (WAV(african)[15e3:45e3:3]*Gain(-6))[0]
    s = s[1::-1]
    audio = s.mixdown(sample_rate=24000, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, test_reverse_channels)

def test_to_stereo_syntax():
    s = Sine()[0:2] # automatically casts into stereo
    s[0] += 0.2*Triangle(frequency=360)
    audio = s.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)

def test_implicit_add_channel():
    s = Sine() #[0:2]
    #s[0] += 0.4*Triangle(duration=6e3) # exceeding signal bounds in time
    s[2] = 0.2*Triangle() # channels it into mono channel with empty R
    #print(s)
    audio = s.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, test_implicit_add_channel)

def test_to_mono():
    s = WAV(african)[15e3:25e3]
    ### s = sum(s) # raises error - we do not know how many channels there are
    s = s[0] + s[1] # use this
    #s *= Mono() # or this
    audio = s.mixdown(sample_rate=24000, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)

def test_reverse_channels_2():
    s = WAV(african)[15e3:25e3]
    s[0], s[1] = s[1], s[0] # this works
    audio = s.mixdown(sample_rate=24000, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)

def test_amplitude_param():
    s = WAV(african)[15e3:25e3]
    c1 = Constant(1, 3e3) | Line(1, 0.01, duration=7e3)
    c2 = SineCurve(frequency=3, depth=0.3, baseline=0.7, duration=10e3)
    s *= Amplitude(c1, c2)
    audio = s.mixdown(sample_rate=24000, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    # export_test(audio, test_amplitude_param)

def test_gain_param():
    s = WAV(african)[15e3:28e3]
    c1 = Line(-80,0,duration=8e3)
    c2 = Line(-40,-6,duration=4e3)
    s *= Gain(c1, c2)
    s[1,4e3:] *= Gain(-6)
    audio = s.mixdown(sample_rate=24000, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    # export_test(audio, test_gain_param)

def test_ADSR():
    notes = [-3, -6, 1, 4, 3, -1, 1, 9, 8, 4, 6]*2
    melody = Signal.concat(*[ Square(frequency=midC(notes[i]), duration=0.5e3)*
                             ADSR(attack=0.03e3, decay=0.1e3, sustain=0.8, release=0.02e3, hold=0.1e3)
                            for i in range(len(notes))])
    melody[1] = Signal.concat(*[ Square(frequency=midC(notes[(i+2)%(len(notes))]), duration=0.5e3)*
                             ADSR(attack=0.03e3, decay=0.1e3, sustain=0.8, release=0.02e3, hold=0)
                            for i in range(len(notes))])
    melody *= Average_samples(5)
    audio = melody.mixdown(sample_rate=24000, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, test_ADSR)






def pan_mono_test():
    c = Constant(-100, 2.5e3) | Line(-100, 100, 5e3)
    s = Sine(duration=10e3)*Pan(c)
    
    audio = s.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, pan_mono_test)

def pan_mono_test2():
    panMax = 100
    panMin = -100
    width = panMax - panMin
    eps = 0.001
    
    panLaw = -6 # -3 seems appropriate for headphones
    time = 8e3
    
    pan_shape = lambda x: np.log((x+panMax)/(width)) # +0.1 to prevent log(0)
    LdB = lambda x: (-panLaw/np.log(2))*pan_shape(x)
    RdB = lambda x: LdB(-x)
    
    L = lambda t: LdB(width*t*1000/time + panMin)
    R = lambda t: RdB(width*t*1000/time + panMin)
    
    # =-===========
    s = Sine(duration=10e3)[0:2]
    s *= Gain(Curve(L, duration=time), Curve(R, duration=8e3))
    
    audio = s.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, pan_mono_test2)

def pan_mono_test3():
    s = Sine(duration=2e3)*Pan(-100)
    s |= Sine(duration=2e3)*Pan(0)
    s |= Sine(duration=2e3)*Pan(100)
    
    c = Line(-100, 100, 5e3) | Logistic(100, -100, duration=5e3)
    s2 = Sine(duration=10e3)*Pan(c)
    
    Pan.panLaw = -6
    audio = s2.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, pan_mono_test3)



def multichannel_test():
    s = Sine(frequency=midC(1))
    s[1] = Sine(frequency=midC(-3))
    s[2] = Sine(frequency=midC(-7))
    s[3] = Sine(frequency=midC(4))
    audio = s.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, multichannel_test)



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




def syntactical_channel_rearrange_test():
    s = WAV(african)[10e3:20e3]
    s[0], s[1] = s[1], s[0]
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)

    
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












if __name__ == "__main__":
    pass
    
    
    
    
    
    
    