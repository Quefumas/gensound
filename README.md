# Gensound
The Python way to Audio processing & synthesis.
* Intuitive
* Flexible
* Lightweight

Do you enjoy experimenting with audio?
Learning about signal processing?
Creating and manipulating sounds?

Gensound is a lightweight library designed for:
* Offline Audio Manipulation & Synthesis
* Musical Experiments
* Electronic Composition

Core features:
* Familiar NumPy syntax is easy to learn and yields clarity, flexibility and conciseness
* Easily extensible - combine new functionalities and effects with zero headache
* Educational - perfect for learning about audio and signals
* Customized panning schemes to enable complex placements of variable number of sound sources
* Parametrization

## What Can It Do?

## One-liners
* Load a WAV file into a `Signal` object:
```python
from Signal import WAV

wav = WAV(filename)
```

* Generate audio stream from `Signal` object:
```python
audio = wav.mixdown(sample_rate=44100, byte_width=2)
```

* Playback or file export:
```python
play_Audio(audio)
export_WAV("test.wav", audio)
```

* Mix a Stereo signal to mono:
```python
wav = 0.5*wav[0] + 0.5*wav[1] # sums up L and R channels together, halving the amplitudes
```

* Reverse L/R channels in stereo WAV file:
```python
wav[0], wav[1] = wav[1], wav[0]
```

* Add a 60Hz sine wave to the left channel of a WAV file, 4 seconds after the beginning:
```python
from gensound import Sine

wav[0,4e3:] += Sine(frequency=60, duration=2e3)*Gain(-9) # mix a sine wav to the L channel, starting at 4000ms
```

* Play the R channel of a WAV file in reverse:
```python
from gensound import Reverse

wav[0] *= Reverse()
```

* Haas effect - delaying the L channel by several samples makes the sound appear to be coming from the right
```python
wav[0] *= Shift(80) # lisen with headphones! try changing the number of samples
```

* Imitate electric guitar amplifier and reverb effect:
```python
from gensound.amplifiers import GuitarAmp_Test
from gensound.effects import OneImpulseReverb

guitar = WAV("guitar_clean.wav")

guitar *= Gain(20)*GuitarAmp_Test(harshness=10, cutoff=4000)*OneImpulseReverb(mix=1.2, num=2000, curve="steep")
```

## Setup
* Install NumPy (any non-ancient version)
* Install the cross-platform, low-dependency [SimpleAudio](https://github.com/hamiltron/py-simple-audio) for audio and WAV file I/O (this may change one day)
* Download `gensound` directory
* To test, download and run `testPackage.py` and enjoy some microtonal harmonies

## Proper Explanations

The library is based on two core classes:
* `Signal` - this represents a stream of multi-channeled samples, either raw (e.g. loaded from WAV file) or mathematically computable (e.g. a Sawtooth wave). Behaves very much like a `numpy.ndarray`.
* `Transforms` - this represents a process that can be applied to a Signal (for example, reverb, filtering, gain, reverse, slicing)

Signals are envisioned as mathematical objects, and the library relies greatly on overloading of arithmetic operations on them, in conjunction with Transforms. All of the following expressions return a modified Signal object:
* `amplitude*Signal`: change Signal's amplitude by a given factor
* `-Signal`: inverts the signal
* `Signal + Signal`: mix two signals together
* `Signal | Signal`: concatenate two signals one after the other
* `Signal**4`: repeat the signal 4 times
* `Signal*Transform`: apply `Transform` to `Signal`
* `Signal[start_channel:end_channel,start_ms:end_ms]`: `Signal` sliced to a certain range of channels and time (in ms). The first slice expects integers; the second expects floats.
* `Signal[start_channel:end_channel,start_sample:end_sample]`: When the second slice finds integers instead of floats, it is interpreted as a range over samples instead of milliseconds. Note that the duration of this signal changes according to the sample rate.
* `Signal[start_channel:end_channel]`: when a single slice of ints is given, it is taken to mean the channels.
* `Signal[start_ms:end_ms]`: if the slice is made up of floats, it is interpreted as timestamps, i.e.: `Signal[:,start_ms:end_ms]`.

> The slice notations may also be used for assignments:
```python
wav[4e3:4.5e3] = Sine(frequency=1e3, duration=0.5e3) # censor beep on seconds 4-4.5
wav[0,6e3:] *= Reverb(...) # add effect to L channel starting from second 6
```

> Slice notation may also be used to increase the number of channels implicitly:
```python
wav = WAV("mono_audio.wav") # mono Signal object
wav[1] = -wav[0] # now a stereo Signal with R being a phase inverted version of L
```

> Note the convention that floats represent time as milliseconds, while integers represent number of samples.

The overloading of basic arithmetic operators means that we can generate complex signals in a Pythonic way:
```python
f = 220 # fundamental frequency
sawtooth = (2/np.pi)*sum([((-1)**k/k)*Sine(frequency=k*f, duration=10e3) for k in range(1,11)])
# approximates a sawtooth wave by the first 10 harmonics
```

After creating a complex Signal object, containing various Signals to which various Transforms may be applied, use the `Signal.mixdown()` method to resolve the Signal into a third core type, `Audio`, which holds an actual stream of samples, which can then be output to disk or speakers. Gensound resolves the Signal by recursively resolving each of the Signals contained within, and applying the Transforms to the result sequentially. There is no need to go deeper into `Audio` objects for now; it's only needed when one wishes to add their custom Signals and Transforms.

## Common Signals & Transforms
See the [Reference](REFERENCE.md) for a list of useful signals and transforms.

## Extreme Examples


## Advanced Topics
Will cover:
* How to extend Signal and Transform to implement new effects
* CrossFades and BiTransforms
* Curves
* Custom Panning Schemes










