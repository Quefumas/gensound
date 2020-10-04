# Class Reference

## Signals

* `Step(duration=1)`: a step signal, equal to 1 for the `duration` samples.

* `WhiteNoise(duration)`: random white noise, having an equal expect energy in all frequencies.

* `Sine(frequency, duration)`: a sine wave.

* `Triangle(frequency, duration)`: a triangle wave.

* `Square(frequency, duration)`: a square wave.

* `Sawtooth(frequency, duration)`: a sawtooth wave.

* `Raw(audio)`: accepts an `Audio` instance
(for example a signal that was mixed-down previously, for incremental composition).

* `WAV(filename)`: loads audio from a WAV file.

> Test Raw

## Transforms

* `Shift(duration)`: delays the signal in time by specified duration. Can also accept negative values.

* `Extend(duration)`: appends silence for the specified duration.

* `Reverse()`: plays the audio in reverse.

* `Gain(*dBs)`: applies the gains to each of the channels.
If one argument is given, it is applied to all channels.

* `Amplitude(*amps)`: applies the amplitudes to each of the channels.
If one argument is given, it is applied to all channels.
In that case it is recommended to simply left-multiply the signal by the amplitude (float),
which is an alias of this transform.

* `Fade(is_in=True, duration)`: linear dB fade in/out to the start/end of signal,
stretching over the desired duration

* `CrossFade(duration)`: a BiTransform, for example `signal1 | CrossFade(duration=0.5e3) | signal2`.
Overlapping crossfade between the two signals.

* `Mono()`: mixes all channels down to one, by summing. Does not normalize.
Preferred usage is by syntax `s = s[0] + s[1] + ...` instead.

* `Pan(pan, scheme=defaultStereo)`: receives a mono signal and outputs a stereo signal.
`pan` argument ranges from -100 to 100, inclusive.
For customizing the default pan law of -3dB, and the panning scheme,
see the appropriate section in the documentation (TODO).

* `Repan(*channels)`: remaps the channels of a signal.
`Repan(1,0)` will switch L/R, `Repan(None, 1)` will silence L, leaving R unchanged.
Preferred usage is by syntax `s[0], s[1] = s[1], s[0]` instead.

* `Downsample(factor, phase=0)`: downsamples the signal by throwing all but one per `factor` samples.
The `phase` argument is for the very specific cases
where it matters which of every `factor` samples should be kept.

* `Convolution(audio)`: accepts a `numpy.ndarray`, `Audio` or WAV filename.
Convolves the audio with the host signal, for example for convolutional reverb.

* `ADSR(attack, decay, sustain, release, hold=0)`: applies ADSR envelope.



> TODO should we include Repan, Mono, Amplitude, Reverse at all?
> How to name AmpFreq, Average_samples

> TODO add guitar amp, one impule reverb, average_samples, ampfreq, FIR, IIR, LPF, HPF for now

















