# -*- coding: utf-8 -*-

import numpy as np

from gensound.utils import isnumber

midA = 440
octave = 2

semitone = np.power(octave, 1/12)
cent = np.power(semitone, 1/100)

logSemitone = lambda k: np.log(k)/np.log(semitone)

midC = lambda s: midA*semitone**(-9+s)

def freq_to_pitch(freq):
    A0 = 27.5 # lowest on piano?
    if freq < A0:
        return "-"
    semitones_above_A0 = logSemitone(freq/A0)
    closest_pitch = int(round(semitones_above_A0))
    #breakpoint()
    divergence = semitones_above_A0 - closest_pitch
    
    octave = (closest_pitch + 9) // 12
    named_pitch = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"][closest_pitch % 12]
    
    return named_pitch + str(octave) + ( ("+" if divergence > 0 else "") + str(int(round(divergence*100))) if round(divergence,2) != 0 else "")

def str_to_freq(f): # this is a hack, better use regex or something else
    """ 'C##4+35' middle C## plus 35 cents
    'A' A4 (octave implied)
    """
    if f in ("r",""):
        return None
    
    cents = 0
    if "+" in f:
        cents = int(f.split("+")[-1])
        f = f.split("+")[0]
    elif "-" in f:
        cents = - int(f.split("-")[-1])
        f = f.split("-")[0]
    
    semi = {"C":0, "D":2, "E":4, "F":5, "G":7, "A":9, "B":11}[f[0]]
    f = f[1:]
    
    while(len(f) > 0 and f[0] in ("#", "b")):
        semi += 1 if f[0] == "#" else -1
        f = f[1:]
    
    if len(f) > 0:
        semi += 12*(int(f)-4) # octave
    
    return midC(semi+cents/100)


import re
INTEGER = r"[0-9]+"
NUMERIC = r"[0-9]+(?:\.[0-9]+)?)"
PITCH = fr"(?P<name>[A-G])(?P<accidentals>b*|#*)(?P<octave>[0-9]|,+|'+)?(?P<cents>(?:\+|-)(?:{INTEGER}))?"
TOKEN_REGEX = re.compile(fr"^(?:(?:{PITCH}|(?P<frequency>{NUMERIC})|(?P<rest>[r])|(?P<repeat>\.))"
                         fr"(?:\=(?P<beats>{NUMERIC})?$")
step_semitones = {"C":0, "D":2, "E":4, "F":5, "G":7, "A":9, "B":11}
"""

Pitch is expressed as <name><accidentals?><octave?><cents?>
<name> is from [A-G],
<accidentals> (optional) could be e.g. "###", "b"
<octave> (optional, default value depends) is either an int (4 = middle octave),
    or apostrophe (') or comma (,) indicating one octave higher or lower than default (which may depend on previous notes!)
<cents> is a sign plus an integer: "+34", "-21"


A note in the sequence is expressed as:
(<pitch> OR <frequency> OR <rest> OR <repeat>)<duration?>

Instead of <pitch> we can use <frequency> (any int/float), <rest> ('r') to indicate rest, or <repeat> ('.') to repeat previous pitch (not yet implemented)

optional duration is "=<int/float>", and will multiply the duration of the internal beat provided elsewhere


"""


def parse_note_params(note_str):
    params = TOKEN_REGEX.match(note_str).groupdict()
    
    # belongs here?
    if params["name"] is not None:
        params["step"] = "CDEFGAB".index(params["name"])
    
    if params["accidentals"] is not None:
        params["accidentals_semitones"] = len(params["accidentals"])*(-1 if "b" in params["accidentals"] else 1)
    else:
        params["accidentals_semitones"] = 0
    
    return params

# TODO make this accessible and modifiable by user
def read_freq(f):
    if isnumber(f):
        return f
    
    if isinstance(f, str):
        return str_to_freq(f)
    
    return f # important for curves

def is_upwards_motion(step1, step2):
    # returns True if the shortest movement between two steps (i.e. C and F) is upwards
    # False otherwise.
    return abs((step2 - step1)%7) < abs((step1 - step2)%7)


def parse_melody_to_signal(melody_str):
    # TODO clean this up and generalise
    """
    Returns list of frequency/beats pairs
    later beats will be multiplied by the given base duration
    """
    # sigCls should be of type Oscillator
    beats = 1
    octave = 4
    previous_frequency = None # for repeats
    last_step = None # for ', octave indications
    
    sigs = []
    
    
    is_cents = True
    transpose_semitones = 0
    mute = False
    
    beat_index = -1
    
    for note in melody_str.split():
        if note == "|": # barline, does nothing
            continue
        
        if note[0] == "@": # modifier
            if note == "@cents_on":
                is_cents = True
            elif note == "@cents_off":
                is_cents = False
            elif note == "@mute":
                mute = True
            elif note == "@unmute":
                mute = False
            elif "@transpose" in note:
                transpose_semitones = float(note.split(":")[1])
            elif "@beat_pattern" in note:
                beats = [float(b) for b in note.split(":")[1].split(",")]
                beat_index = -1
            
            continue
        
        # parse note token
        note = parse_note_params(note)
        
        # infer beat
        cur_beat = None
        
        if note["beats"] is not None:
            beats = float(note["beats"])
            cur_beat = beats
            beat_index = -1
        else:
            if isinstance(beats, list):
                beat_index = (beat_index + 1) % len(beats)
                cur_beat = beats[beat_index]
            else:
                cur_beat = beats
        
        # deal with rests
        if note["rest"] is not None:
            sigs.append({"frequency": "r", "beats": cur_beat})
            continue
        
        # deal with repeat TODO
        #if note["repeat"] is not None:
        #    sigs.append({"frequency": previous_frequency, "beats": beats})
        
        # note given as frequency
        if note["frequency"] is not None:
            previous_frequency = float(note["frequency"])
            sigs.append({"frequency": previous_frequency, "beats": cur_beat})
            continue
        
        # note given as pitch class
        if note["octave"] is not None and note["octave"] in "0123456789":
            octave = int(note["octave"])
        else: # None or ',
            # infer octave from steps
            if last_step is None: # didn't specify octave on the first note, assume 4
                last_step = note["step"]
                
            if is_upwards_motion(last_step, note["step"]):
                if note["step"] < last_step:
                    octave += 1
            else:
                if note["step"] > last_step:
                    octave -=1
            
            if note["octave"] is not None:
                if "'" in note["octave"]:
                    octave += len(note["octave"])
                elif "," in note["octave"]:
                    octave -= len(note["octave"])
        
        if note["cents"] is None:
            note["cents"] = "0"
        
        last_step = note["step"]
        
        semitones = 12*(octave-4) + step_semitones[note["name"]] + note["accidentals_semitones"]
        
        if is_cents:
            semitones += int(note["cents"])/100
        
        semitones += transpose_semitones
        
        previous_frequency = midC(semitones)
        
        sigs.append({"frequency": previous_frequency if not mute else "r", "beats":cur_beat})
        
        
    return sigs























