# Gensound
The Python way to audio processing & synthesis. 

An intuitive, flexible and lightweight library for:
* Experimenting with audio and signal processing
* Creating and manipulating sounds
* Electronic composition

Core features:
* Platform independent
* Very intuitive syntax
* Easy to create new effects or experiments and combine them with existing features
* Great for learning about audio and signals
* Multi-channel audio for customizable placement of sound sources
* Parametrization
* And more to come!

## Setup

1. Install using `pip install gensound`.
This will install NumPy and [SimpleAudio](https://github.com/hamiltron/py-simple-audio), if needed.

2. Run the examples below (or some of the example files in the repository).

## Gensound in less than a minute
All audio is a mixture of signals (audio streams), to which we can apply transforms (effects).
* To apply a transform to a signal we use the syntax: `Signal * Transform`;
* To mix two signals together we use addition: `Signal + Signal`;
* And to concatenate two signals (play one after the other): `Signal | Signal`.

Each of these operations results in a new `Signal` object on which we can perform more of these operations.

Now, let's run some basic examples!

## Show Me the Code
* Load a WAV into a `Signal` object from a file:
```python
from gensound import WAV, test_wav

wav = WAV(test_wav) # load sample WAV, included with gensound
```

* Playback or file export:
```python
wav.play()
wav.export("test.wav")
```

* Play file using different sample rate (results in pitch shift):
```python
wav.play(sample_rate=32000) # original sample rate 44.1 kHz
```

* Play only the R channel:
```python
wav[1].play() # wav[0] is L channel, wav[1] is R
```

* Turn down the volume of L channel:
```python
wav[0] *= 0.5 # amplitude halved; wav[1] amplitude remains the same
wav.play()
```

* Same thing, but using dBs:
```python
from gensound import Gain
wav[0] *= Gain(-3) # apply Gain transform to attenuate by 3 dB
```

* Mix a Stereo signal (L-R channels) to mono (center channel only):
```python
wav = 0.5*wav[0] + 0.5*wav[1] # sums up L and R channels together, halving the amplitudes
```

* Switch L/R channels:
```python
wav[0], wav[1] = wav[1], wav[0]
```

* Crop 5 seconds from the beginning (`5e3` is short for `5000.0`, meaning 5,000 milliseconds or 5 seconds):
```python
wav = wav[5e3:] # since 5e3 is float, gensound knows we are not talking about channels
```
If we only care about the R channel:
```python
wav = wav[1, 5e3:] # 5 seconds onwards, R channel only
```
We can decide to slice using sample numbers (ints) instead of absolute time (floats):
```python
wav = wav[:,:1000] # grabs first 1000 samples in both channels; samples are in ints
```

* Repeat a signal 5 times:
```python
wav = wav**5
```

* Mix a 440Hz (middle A) sine wave to the L channel, 4 seconds after the beginning:
```python
from gensound import Sine

wav[0,4e3:] += Sine(frequency=440, duration=2e3)*Gain(-9)
```

* Play a tune (see full syntax [here](https://github.com/Quefumas/gensound/wiki/Melodic-Shorthand-Notation)):
```python
s = Sine('D5 C# A F# B G# E# C# F#', duration=0.5e3)
s.play()
```

* Reverse the R channel:
```python
from gensound import Reverse

wav[1] *= Reverse()
```

* [Haas effect](https://en.wikipedia.org/wiki/Precedence_effect) - delaying the L channel by several samples makes the sound appear to be coming from the right:
```python
from gensound import Shift

wav[0] *= Shift(80) # try changing the number of samples
# when listening, pay attention to the direction the audio appears to be coming from
```

* Stretch effect - slowing down or speeding up the signal by stretching or shrinking it. This affects pitch as well:
```python
from gensound.transforms import Stretch

wav *= Stretch(rate=1.5) # plays the Signal 1.5 times as fast
wav *= Stretch(duration=30e3) # alternative syntax: fit the Signal into 30 seconds
```



* Advanced: AutoPan both L/R channels with different frequency and depth:
```python
from gensound.curve import SineCurve

s = WAV(test_wav)[10e3:30e3] # pick 20 seconds of audio

curveL = SineCurve(frequency=0.2, depth=50, baseline=-50, duration=20e3)
# L channel will move in a Sine pattern between -100 (Hard L) and 0 (C)

curveR = SineCurve(frequency=0.12, depth=100, baseline=0, duration=20e3)
# R channel will move in a Sine pattern (different frequency) between -100 and 100
    
t = s[0]*Pan(curveL) + s[1]*Pan(curveR)
```


## Syntax Cheatsheet

Meet the two core classes:
* `Signal` - a stream of multi-channeled samples, either raw (e.g. loaded from WAV file) or mathematically computable (e.g. a Sawtooth wave). Behaves very much like a `numpy.ndarray`.
* `Transform` - any process that can be applied to a Signal (for example, reverb, filtering, gain, reverse, slicing).

**By combining Signals in various ways and applying Transforms to them, we can generate anything.**

Signals are envisioned as mathematical objects, and Gensound relies greatly on overloading of arithmetic operations on them, in conjunction with Transforms.
All of the following expressions return a new Signal object:
* `amplitude*Signal`: change Signal's amplitude (loudness) by a given factor (float)
* `-Signal`: inverts the Signal
* `Signal + Signal`: mix two Signals together
* `Signal | Signal`: concatenate two Signals one after the other
* `Signal**4`: repeat the Signal 4 times
* `Signal*Transform`: apply `Transform` to `Signal`
* `Signal[start_channel:end_channel,start_ms:end_ms]`: `Signal` sliced to a certain range of channels and time (in ms). The first slice expects integers; the second expects floats.
* `Signal[start_channel:end_channel,start_sample:end_sample]`: When the second slice finds integers instead of floats, it is interpreted as a range over samples instead of milliseconds.
   Note that the duration of this Signal changes according to the sample rate.
* `Signal[start_channel:end_channel]`: when a single slice of ints is given, it is taken to mean the channels.
* `Signal[start_ms:end_ms]`: if the slice is made up of floats, it is interpreted as timestamps, i.e.: `Signal[:,start_ms:end_ms]`.

The slice notations may also be used for assignments:
```python
wav[4e3:4.5e3] = Sine(frequency=1e3, duration=0.5e3) # censor beep on seconds 4-4.5
wav[0,6e3:] *= Vibrato(frequency=4, width=0.5) # add vibrato effect to L channel starting from second 6
```

...and to increase the number of channels implicitly:
```python
wav = WAV("mono_audio.wav") # mono Signal object
wav[1] = -wav[0] # now a stereo Signal with R being a phase inverted version of L
```

> Note the convention that floats represent time as milliseconds, while integers represent number of samples.

<!--
The overloading of basic arithmetic operators means that we can generate complex signals in a Pythonic way:
```python
f = 220 # fundamental frequency
sawtooth = (2/np.pi)*sum([((-1)**k/k)*Sine(frequency=k*f, duration=10e3) for k in range(1,11)])
# approximates a sawtooth wave by the first 10 harmonics
```
-->

When performing playback or file export of a Signal,
Gensound resolves the Signal tree recursively, combining the various Signals and applying the transforms.

## More
I would love to hear about your experience using Gensound - what worked well, what didn't, what do you think is missing.
Don't hesitate to [drop me a line](https://github.com/Quefumas/gensound/discussions).

The [Wiki](https://github.com/Quefumas/gensound/wiki) is planned to become the definitive user guide,
and will also provide many fun examples to learn and play with.
In the meanwhile you are also welcome to look at the [Reference](REFERENCE.md) for a growing list of useful signals and transforms.
To get a better understanding of the underlying code, you are invited to the [Technical Guide](TECHNICAL.md).
If you are interested in contributing, check out [Contribution](CONTRIBUTING.md).


## Topics not yet covered
* How to extend Signal and Transform to implement new effects
* Crossfades and BiTransforms
* Curves and parametrization
* Custom Panning Schemes










