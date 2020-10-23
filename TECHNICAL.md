# A Technical Introduction

This document helps developers understand how the code works;
casual users of the library have little need for the information here.
This assumes basic familiarity with NumPy, arithmetics, audio and the library syntax.

## Core Operations

The core of the library can be summed up in the functionality of the following 3 classes.
`Signal` and `Transform` are basically shells that implement these operations,
and they are extended by the classes that will actually generate and process the audio.

* `Audio` is more or less a wrapper for an `numpy.ndarray` instance (`Audio.audio`),
and should be relatively invisible to common users.
* `Signal` generates an `Audio` instance using the overridable `Signal.generate()`.
  There are 3 main operations involving `Signal` instances:
  * `Signal._mix(self, other)` mixes another signal into `self` (basically vector addition).
    The two signals don't have to share the same length.
  * `Signal._concat(self, other)` concatenates another signal to `self` (vector concatenation).
  * `Signal._apply(self, transform)` applies a `Transform` instance to the signal (see next).
* `Transform` can represent any conceivable transformation on a given `Audio` instance,
using the overridable `Transform.realise(self, audio)`. This method changes `audio` directly.

Next, arithmetical operators are overloaded to perform some of the above operations.
All of these return a new instance of `Signal`:
* `Signal + Signal` mixes them both, returning a new instance of `Signal`.
* `Signal | Signal` concatenates them both, returning a new instance of `Signal`.
* `Signal**2` is equivalent to `Signal | Signal`.
* `Signal*Transform` applies `Transform` to `Signal`.

These operations are implemented internally using two sub-classes of `Signal`
which are invisible to the casual user:
* `Mix` receives as arguments a list of `Signal` instances,
and upon `Mix.generate()`, calls `generate` for each of these, and returns the sum.
* `Sequence` does the same for the concatenation operator: it calls `generate()`
for each of the arguments, concatenating them in order.
Finally, The apply operation is performed simply
by appending the transform to the `Signal.transforms` list.
> Should they be renamed to `_Mix`,`_Sequence`?

For transforms there is a similar class, `TransformChain`,
which allows us to save a product of transforms, which will be later applied to a signal.


## The Mixdown Tree

In ordinary use-cases, the user will generate a top-level `Signal` instance,
which is made up of concatenations and mixes of various signals,
to which various transforms are applied.
In fact, we can think of the resulting mix as a tree, where each node is a `Signal` instance,
which carries its own transforms.
If this node has any children, that would mean it is either `Mix` or `Sequence`,
which represent some combination of simpler signales.
Leafs are typically elmentary signals, such as a WAV file or Sine wave.

Most of the code will be spent designing this tree,
using operations such as mix, concatenate and apply.
This will result in an actual tree of signals,
which may be printed in human-readable form using `print()`.
At this point, no audio has been generated at all!

Once the mix tree, or top-level signal, is prepared,
use the method `Signal.mixdown(self, sample_rate, byte_width=2, max_amplitude=1)` 
which returns an `Audio` instance of the result, which can be played back or exported as WAV.
Mixdown is performed recursively, where the internal nodes (Mix/Sequence)
call the `realise` methods of each of the descendents,
which return `Audio` objects, and then combine them in the desired way,
while the leaves' `realise` methods generate actual `Audio`
instances by themselves (such as a sine wave).

The `realise` method actually does 2 things:
1. It calls `self.generate` to generate the signal audio itself, whether it be
an elementary signal such as a sine wave, or a compound signal such as `Mix`.
2. It applies all transforms in `self.transforms` to the audio, in order.

Step 2 is not included in `Signal.generate` since this way there is minimal headache
when creating new signals by hand: one only needs to override `generate`,
and the transforms will be applied automatically to the new signal behind the scenes.




## Slicing and Shifting

We now do further piggybacking on NumPy syntax,
letting signals be treated similarly to `numpy.ndarray` instances:
`s[0:2,3e3:4e3]` should return the 4th second of the first 2 channels of `s`,
and as a `Signal` instance as well.
Furthermore, this syntax should support applying transforms to selected parts of the signal,
and also mixing into parts of a signal, or replacing them entirely.

These features are implemented using two invisible transforms:
* `Slice` receives a channel slice and a time slice as arguments.
When the signal on which it is applied invokes `Slice.realise`,
the latter simply slices the already-generated audio according to these arguments.
* `Combine` receives the same arguments, in addition to a signal.
On `realise`, it generates this signal's audio and places it in the correct position
in the audio which it received from its host signal.

Further implementation comments:
* When applying a transform on a slice (i.e. `s[0]*=Reverb()`),
a sliced version of the original signal is created, to which the transform is applied,
and is then fed into `Combine`.
* When a long signal is placed into a short slice, it can spill into the rest of the audio.
This is the desired behaviour.
Preventing it is easy: just slice the inserted audio to be as long as the slice.
* The static `Signal.__subscripts` deals with the channel/time slices,
which includes converting float time slices to samples and deciding between channel/time
when only one slice is given.

> Could it be that using invisible Signals such as Mix and Sequence can accomplish
> the same but in a cleaner way?


Another transform which messes with the internal mix process is `Shift`,
which enables delaying a signal by a specified amount of samples or milliseconds.
Since padding audio instances with zeros may be wasteful, each such instance
keeps a local variable `shift`, representing the total shift with respect to its
current starting position.
When mixing a signal with non-zero shift into another,
this shift is taken into account.
Note that negative shift is also possible!

> TODO fully describe desired shift behaviour and ensure it is implemented correctly


## Finer details, open issues and conventions



The length of `audio.shape` is always 2, even for mono signals.
Currently an `Audio` instance contains all you need to playback a piece of audio,
therefore it is also aware of the sample rate (this may change).
Information like byte width does not belong here; that is chosen when outputting.

> At least the 2nd subscript (time) implicitly supports the `step` argument of a slice,
> so we can write `s[4e3:5e3:2]`, which results in shorter audio,
> or `s[4e3:5e3:-1]` which reverses the audio.
> So far this is considered more a feature than a bug.

> What happens/should happen when we try to concatenate into a part of a signal?


In order to implement Crossfades, we use `BiTransform`, a special subclass of Transform,
which may affect two signals concatenated together
(as opposed to `Transform`, which may be applied to a single Signal).
BiTransform holds two TransformChain instances, for the preceding and following signals.
Upon Concatenation, i.e. `signal1 | CrossFade(duration=0.5e3) | signal2`,
it applies one Fade to the left-concatenated signal, and another to the right.

IIRC, this is possible event when omitting the second signal,
i.e. the expression `signal1 | CrossFade(duration=0.5e3)` is valid,
and will behave correctly even when concatenating the second signal later in the code.


## Curves and Parametrization, Custom Panning Schemes

TODO








