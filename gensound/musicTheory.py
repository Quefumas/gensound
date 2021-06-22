# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 09:24:24 2019

@author: Dror
"""

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
    
    return named_pitch + str(octave) + (" " + ("+" if divergence > 0 else "") + str(int(round(divergence*100))) if round(divergence,2) != 0 else "")

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
PITCH_REGEX = re.compile(r"^(?:(?:(?P<name>[A-G])(?P<accidentals>b*|#*)(?P<octave>[0-9]|,+|'+)?(?P<cents>(?:\+|-)(?:[0-9]+))?)|(?P<rest>[r])|(?P<repeat>\.))"
                         r"(?:\=(?P<beats>[0-9]+(?:\.[0-9]+)?))?$")
step_semitones = {"C":0, "D":2, "E":4, "F":5, "G":7, "A":9, "B":11}
"""

Pitch is expressed as <name><accidentals?><octave?><cents?>
<name> is from [A-G],
<accidentals> (optional) could be e.g. "###", "b"
<octave> (optional, default value depends) is either an int (4 = middle octave),
    or apostrophe (') or comma (,) indicating one octave higher or lower than default (which may depend on previous notes!)
<cents> is a sign plus an integer: "+34", "-21"


A note in the sequence is expressed as:
(<pitch> OR <rest> OR <repeat>)<duration?>

Instead of <pitch> we can use <rest> ('r') to indicate rest, or <repeat> ('.') to repeat previous pitch

optional duration is "=<int or decimal>", and will multiply the duration of the internal beat provided elsewhere


"""


def parse_note_params(note_str):
    params = PITCH_REGEX.match(note_str).groupdict()
    
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
    """
    Returns list of frequency/beats pairs
    later beats will be multiplied by the given base duration
    """
    # sigCls should be of type Oscillator
    beats = 1
    octave = 4
    last_pitch = None # for repeats
    last_step = None # for ', octave indications
    
    sigs = []
    
    
    for note in melody_str.split():
        if len(note) == 0:
            continue
        
        note = parse_note_params(note)
        
        # TODO deal with repeat or rest
        
        if note["beats"] is not None:
            beats = float(note["beats"])
        
        if note["rest"] is not None:
            sigs.append({"frequency": "r", "beats": beats})
            continue
        
        if note["repeat"] is not None:
            sigs.append({"frequency": last_pitch, "beats": beats})
        
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
        
        semitones = step_semitones[note["name"]] + 12*(octave-4) + note["accidentals_semitones"] + int(note["cents"])/100
        last_pitch = midC(semitones)
        
        sigs.append({"frequency": last_pitch, "beats":beats})
        
        
    return sigs























