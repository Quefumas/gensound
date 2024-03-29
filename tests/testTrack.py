# -*- coding: utf-8 -*-
"""

This is for internal purposes; many errors due to changing code!

"""

import numpy as np

from gensound.signals import Signal, Sine, Square, Triangle, Sawtooth, WhiteNoise, WAV, Step
from gensound.transforms import Fade, SineAM, Shift, Pan, Extend, \
                       Amplitude, \
                       Reverse, Repan, Gain, Limiter, Convolution, Slice, \
                       Mono, ADSR, CrossFade
# from gensound.filters import MovingAverage, LowPassBasic, Butterworth, IIR_basic, \
#                     IIR_general, IIR_OnePole, IIR_OnePole_LowPass, IIR_OnePole_HighPass
#from gensound.amplifiers import GuitarAmp_Test
from gensound.curve import Curve, Constant, Line, Logistic, SineCurve, MultiCurve
from gensound.io import export_test # better than export_WAV for debugging

from gensound.musicTheory import midC, semitone

african = "../data/african_sketches_1.wav"
gtrcln = "../data/guitar_clean.wav"

### for testing filters

def SweepTest(stay=0.5e3, step=0.5e3): # start at really low A
    start = 55
    octaves = 4
    c = Constant(start, stay)
    
    for octave in range(octaves):
        c |= Line(start, start*semitone**4, step) | Constant(start*semitone**4, stay)
        start *= semitone**4
        c |= Line(start, start*semitone**3, step) | Constant(start*semitone**3, stay)
        start *= semitone**3
        c |= Line(start, start*semitone**5, step) | Constant(start*semitone**5, stay)
        start *= semitone**5
    
    return Sine(frequency=c, duration=(step+stay)*3*octaves+stay)
#########

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
    #s = WAV(african)[10e3:20e3]
    c = Line(55,110, 3e3) | Constant(110,2e3)
    c |= Line(110, 220, 3e3) | Constant(220, 2e3)
    c |= Line(220, 440, 3e3) | Constant(440, 2e3)
    c |= Line(440, 880, 3e3) | Constant(880, 2e3)
    c |= Line(880, 2*880, 3e3) | Constant(2*880, 2e3)
    s = Sine(frequency=c, duration=20e3)[0:2]
    s[1] *= Butterworth(cutoff=880)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, Butterworth_test)

def Butterworth_experiment():
    s = WAV(african)[10e3:25e3]
    s1 = s[0]*Butterworth(cutoff=880)
    c = Line(-100, 100, 13e3)
    s2 = s[1]*Pan(c)
    t = s1[0:2] + s2
    audio = t.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    # export_test(audio, Butterworth_experiment)

def additive_complex_sound_test():
    def s(f, duration):
        return sum([(1/i**1.5)*Sine(frequency = f*i, duration=duration)*ADSR((0.01e3)*(i), 0.8, 0.5+(1/(i+2)), 0.02e3) for i in range(1, 20)])
    
    freqs = [midC(-3), midC(1), midC(-4), midC(4), midC(6), midC(2), midC(-1), midC(11)]*2
    duration = 1e3
    
    t = Signal.concat(*[s(f, duration) for f in freqs])
    
    audio = t.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, additive_complex_sound_test)

def IIR_basic_test():
    s = WAV(african)[10e3:20e3]
    s[5e3:] *= IIR_basic() # y(n) = 0.3*x(n) + 0.7*y(n-1)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    # play_Audio(audio)
    export_test(audio, IIR_basic_test)

def IIR_general_test():
    s = WAV(african)[10e3:20e3]
    s[3e3:] *= IIR_general([0,  -0.5,0,0],
                           [0.25, 0.15,0.07,0.03])
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    # play_Audio(audio)
    export_test(audio, IIR_general_test)

def IIR_one_pole_test():
    s = WAV(african)[10e3:20e3]
    
    Fc = 880/44100
    b1 = np.e**(-2*np.pi*Fc)
    s[:,:5e3] *= IIR_OnePole(1-b1, b1)
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, IIR_one_pole_test)

def IIR_one_pole_filters_test():
    s = WAV(african)[10e3:20e3]
    
    s[:5e3] *= IIR_OnePole_LowPass(880)
    s[5e3:] *= IIR_OnePole_HighPass(440)
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, IIR_one_pole_filters_test)

def sweep_test():
    s = SweepTest()
    #s *= Butterworth(cutoff=440)
    audio = s.play(max_amplitude=0.2)

def test_transform_chain():
    s = WAV(african)[10e3:20e3]
    t = MovingAverage(5) * Fade(duration=0.5e3)
    t *= Gain(Line(0,-10,3e3) | Line(-10, 0, 5e3))
    s *= t
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)


def test_negative_shift():
    s = WAV(african)[10e3:20e3]
    s = s[:5e3] | s[5e3:]*Shift(-2.5e3)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    #export_test(audio, test_negative_shift)
    play_Audio(audio)

def test_negative_shift_combine():
    s = WAV(african)[10e3:20e3]
    s[5e3:] = s[5e3:]*Shift(1e3)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    export_test(audio, test_negative_shift_combine)
    #play_Audio(audio)


def crossfade_bitransform_syntax_test():
    s = WAV(african)[10e3:20e3]
    s = s[:5e3] | CrossFade(duration=0.5e3) | s[5e3:]
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    # now with linear amp fade, not db linear fade
    #export_test(audio, crossfade_bitransform_syntax_test)

def guitar_amp_test():
    s = WAV(gtrcln)*Gain(20)*GuitarAmp_Test(harshness=10,cutoff=4000)
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    export_test(audio, guitar_amp_test)

def one_impulse_reverb_test():
    from gensound.effects import OneImpulseReverb
    s = WAV(african)[10e3:20e3]*OneImpulseReverb(mix=1.2, num=2000, curve="steep")
    s.play(44100, max_amplitude=0.2)
    export_test(s.mixdown(44100), one_impulse_reverb_test)


def next_gen_parse_osc_melody_test():
    from gensound import Square, Signal
    sig = Square
    
    t = 0.5e3
    
    v1 = sig("C3 Eb F G F Eb "*10, duration=t)
    v2 = sig("Eb4=3 Bb "*10, duration=t)
    v3 = sig("G4=2 A D, "*10, duration=t)
    
    s = Signal()
    s[0] = v2
    s[1] = v3
    s += 0.5*v1
    export_test(s.mixdown(44100), next_gen_parse_osc_melody_test)
    

def test_beat_pattern():
    sig = Triangle
    beat = 1e3
    
    s = sig("@beat_pattern:0.5,0.5,0.33,0.33,0.34,0.5,0.5,0.2,0.2,0.2,0.2,0.2 " + \
            " D C# F#, B E G# B A# F# D# E# "*4,
            beat)
    b = sig("@beat_pattern:0.41,0.41 " + \
            " B2 D "*18,
            beat)
    (s+b).play()

def test_plot_audio():
    from gensound import test_wav
    #w = WAV(test_wav)[20e3:20.5e3]
    
    #w = Sine(220, 0.05e3) + 0.2*Sine(370, 0.05e3)
    w = Square(220, 0.1e3) + 0.3*Triangle(370, 0.1e3) # alien script
    #w = Square(220, 0.05e3) | Triangle(370, 0.05e3)
    a = w.realise(44100)
    a.plot()

def chorale_example():
    sig = Triangle # Square?
    
    beat = 0.5e3 # 120 bpm
    fermata = 0.1 # make fermatas in the melody slightly longer
    pause = 0.6 # and breathe for a moment before starting the next phrase
    
    s = sig(f"r D5 D=2 C#=1 B-13=2 A=1 D E=2 F#-13={2+fermata} r={pause} F#=1 F#=2 F#=1 E=2 F#-13=1 G F#-13=2 E={2+fermata} r={pause} "
            f"D+16=1 E=2 F#-13=1 E=2 D+16=1 B-13 C#=2 D+9={2+fermata} r={pause} A'=1 F#-13=2 D+16=1 E=2 G=1 F#-13 E=2 D=3", beat)
    a = sig(f"r A4 B-16=2 A+16=1 G=2 F#-13=1 F# B-13 A A={2+fermata} r={pause} C#=1 B=2 B=1 B A A A D A A={2+fermata} r={pause} "
            f"B=1 A=2 A=1 B-13 A=0.5 G F#=1 B-13 B A#-13 B={2+fermata} r={pause} A=1 A=2 B=1 A=2 A=1 A B-13 A F#-13=3", beat)
    t = sig(f"r F#4-13 F#=2 F#=1 D=2 D=1 D D C#-13 D={2+fermata} r={pause} C#=1 D+16=2 D+16=1 D C#-13 D E A, D C#-13={2+fermata} r={pause} "
            f"F#=1 E=2 D=1 D C#-13 D+16 D G+5 F# F#={2+fermata} r={pause} E=1 F#-13=2 F#=1 E=2 C#-13=1 A B C#-13 D=3", beat)
    b = sig(f"r D3 B-16 D F# G B-13 D B-16 G A D,={2+fermata} r={pause} A#'-13=1 B=2 A=1 G#-13 A F#-13 C#-13 D F#-13 A={2+fermata} r={pause} "
            f"B=1 C#-13=2 D=1 G, A B G E F# B,={2+fermata} r={pause} C#'-13=1 D C# B C#-13 B A D G, A D,=3", beat)
    
    chorale = s*Pan(25) + b*Pan(-25) + t*Pan(80) + a*Pan(-80)
    
    from gensound.filters import MovingAverage
    chorale *= MovingAverage(5)#*Reverse()
    #export_test(chorale.mixdown(44100), chorale_example)
    chorale.play() # can you spot the parallel octaves?

if __name__ == "__main__":
    #Butterworth_experiment()
    #additive_complex_sound_test()
    #IIR_general_test()
    #sweep_test()
    #one_impulse_reverb_test()
    #next_gen_parse_osc_melody_test()
    #chorale_example()
    #test_beat_pattern()
    test_plot_audio()
    
    # custom_pan_scheme_test() # come back to this?
    #%%%%%
    ...
















