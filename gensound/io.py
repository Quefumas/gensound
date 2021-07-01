# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 19:03:28 2019

@author: Dror

This file contains the entire interface of the library with the OS.
This includes reading and writing files, and real-time playback.

All of these functionalities should be enclosed in this file,
so as to facilitate cross-platform functionality in the future.

This supports the following basic functionalities:
    * playback from Audio instance
    * Audio instance to file (whatever format possible)
    * file to Audio instance

There is a class for each supported I/O library, which provides these functions
for that library in particular. When this file is loaded, the desired libraries
are determined from settings.py (TODO).


Note: The names defined below should only be imported in audio.py.
The Audio class is the final intermediary between Gensound and the actual IO.


"""

import inspect
import time
import random
import string
import datetime

import numpy as np
from gensound.settings import _supported, _supported_bin



# resulting filename when internally converting to WAV
def converted_file_naming_scheme(filename): return ".".join(filename.split(".")[:-1]) + ".wav"


_temporary_folder = "gensound_temp"

def temp_file_naming_scheme():
    # ugly filenames for temp file to prevent accidental overwriting
    nonce = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
    return f"{_temporary_folder}/gensound_temp_{timestamp}_{nonce}.wav"

def file_exists(filename):
    import pathlib
    return pathlib.Path(filename).is_file()




# we start with the support for the various libraries,
# put the exported functionality down below

class _IO_wave:
    name = "wave"
    is_supported = True # python built-in
    
    @staticmethod
    def export_WAV(filename, audio):
        import wave
        
        file = wave.open(filename, "wb")
        file.setnchannels(audio.num_channels)
        file.setsampwidth(audio.byte_width)
        file.setframerate(audio.sample_rate)
        file.setnframes(audio.length)
    
        file.writeframes(audio.buffer)
    
    @staticmethod
    def WAV_to_Audio(filename):
        import wave
        
        with wave.open(filename, "rb") as file:
            buffer = np.frombuffer(file.readframes(file.getnframes()),
                                   [np.uint8,np.int16,None,np.int32][file.getsampwidth()-1])
            buffer = buffer.astype(np.float64)
            
            buffer = np.reshape(buffer,
                                newshape=(file.getnchannels(),
                                          int(len(buffer)/file.getnchannels()))[::-1]).T.copy(order='C')
            buffer /= 2**(8*file.getsampwidth()-1)
            
            from gensound.audio import Audio
            audio = Audio(file.getframerate())
            audio.from_array(buffer)
        
        return audio

class _IO_aifc:
    name = "aifc"
    is_supported = True # python built-in
    
    @staticmethod
    def export_AIFF(filename, audio):
        import aifc
        
        with aifc.open(filename, "wb") as file:
            file.setnchannels(audio.num_channels)
            file.setsampwidth(audio.byte_width)
            file.setframerate(audio.sample_rate)
            file.setnframes(audio.length)
            
            file.writeframes(audio.buffer.byteswap()) # AIFF byteswap
    
    @staticmethod
    def AIFF_to_Audio(filename):
        # when making changes, consider WAV_to_Audio as well
        import aifc
        
        with aifc.open(filename, "rb") as file:
            buffer = np.frombuffer(file.readframes(file.getnframes()),
                                   [np.uint8,np.int16,None,np.int32][file.getsampwidth()-1])
            buffer = buffer.byteswap().astype(np.float64) # byte swap for AIFF only, not WAV
            
            buffer = np.reshape(buffer,
                                newshape=(file.getnchannels(),
                                          int(len(buffer)/file.getnchannels()))[::-1]).T.copy(order='C')
            buffer /= 2**(8*file.getsampwidth()-1)
            
            from gensound.audio import Audio
            audio = Audio(file.getframerate())
            audio.from_array(buffer)
            
        return audio
    

class _IO_SA:
    name = "simpleaudio"
    is_supported = "simpleaudio" in _supported
    
    @staticmethod
    def playback(audio, is_wait=True): # plays Audio instance
        import simpleaudio as sa
        #audio.buffer = audio.buffer.copy(order='C')
        play_obj = sa.play_buffer(audio.buffer,
                                  num_channels=audio.num_channels,
                                  bytes_per_sample=audio.byte_width, # TODO should Audio store this?
                                  sample_rate=audio.sample_rate)
        
        if not is_wait or audio.audio.shape[1] > 3*10**5:
            input("Type something to quit.")
            play_obj.stop()
        else:
            play_obj.wait_done()
    
    @staticmethod
    def WAV_to_Audio(filename=""):
        import simpleaudio as sa
        print("Deprecated SA Wav_to_Audio")
        wav = sa.WaveObject.from_wave_file(filename)
        # TODO support int24
        buffer = np.frombuffer(wav.audio_data, [np.uint8,np.int16,None,np.int32][wav.bytes_per_sample-1]).astype(np.float64)
        
        buffer = np.reshape(buffer,
                            newshape=(wav.num_channels,
                                      int(len(buffer)/wav.num_channels))[::-1]).T.copy(order='C')
        buffer /= 2**(8*wav.bytes_per_sample-1)
        # TODO the above needs some consideration
        # should we convert to float immediately, or wait till the last minute?
        # is this the right place to convert?
        # and should this be normalized in some way in relation to the synthesized signals?
        from gensound.audio import Audio
        audio = Audio(wav.sample_rate)
        audio.from_array(buffer)
        
        return audio

class _IO_ffmpeg:
    name = "ffmpeg"
    is_supported = "ffmpeg" in _supported_bin
    
    @staticmethod
    def file_to_Audio(filename, *args, **kwargs):
        import os
        
        new_name = converted_file_naming_scheme(filename)
        
        if file_exists(new_name):
            print(f"File {os.getcwd()}\{new_name} already exists and will be used instead of converting.")
            return _IO_wave.WAV_to_Audio(new_name)

        import subprocess
        
        args = ['ffmpeg', '-i', filename, new_name]
        
        process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) 
        out, err = process.communicate(None)
        retcode = process.poll()
        
        if retcode:
            print(f"FFMPEG error when converting file {os.getcwd()}\{filename}.")
            return None
        
        print(f"Converted to WAV using FFMPEG: {os.getcwd()}\{new_name}.")
        
        return _IO_wave.WAV_to_Audio(new_name)
    
    @staticmethod
    def export_file(filename, audio):
        # TODO get format from filename or from caller?
        import subprocess
        
        fmt = ["u8", "s16le", "s24le", "s32le"][audio.byte_width-1]
        
        
        args = ['ffmpeg', '-f', fmt, '-ac', str(audio.num_channels), '-i', 'pipe:', filename, '-y']
        
        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process.stdin.write(audio.buffer)
        process.stdin.close()
        
        #out = process.stdout.read() # use stdout=subprocess.PIPE above for this
        #err = process.stderr.read()
        
        #print(out)
        #print(err)
        
        
class _IO_ffmpeg_python:
    name = "ffmpeg-python"
    is_supported = "ffmpeg-python" in _supported
    
    @staticmethod
    def file_to_Audio(filename):
        import ffmpeg, os
        
        new_name = converted_file_naming_scheme(filename)
        
        if file_exists(new_name):
            print(f"File {os.getcwd()}\{new_name} already exists and will be used instead of converting.")
            return _IO_wave.WAV_to_Audio(new_name)
        
        ffmpeg.input(filename).output(new_name).run(quiet=True)
        
        return _IO_wave.WAV_to_Audio(new_name)
    
    @staticmethod
    def export_file(filename, audio):
        # TODO get format from filename or from caller?
        import ffmpeg
        
        # combine this with similar code in ffmpeg class
        fmt = ["u8", "s16le", "s24le", "s32le"][audio.byte_width-1]
        
        process = (ffmpeg.input("pipe:", format=fmt, ac=audio.num_channels)
                    .output(filename)
                    .overwrite_output()
                    .run_async(pipe_stdin=True, quiet=True))
        process.stdin.write(audio.buffer)
        process.stdin.close()
        process.wait()
        ...


class _IO_playsound: # https://github.com/TaylorSMarks/playsound
    name = "playsound"
    is_supported = "playsound" in _supported
    
    @staticmethod
    def playback(audio, *args, **kwargs): # TODO also has "block" arg which may be nice
        import os
        filename = temp_file_naming_scheme()
        
        os.makedirs(_temporary_folder, exist_ok=True)
        
        _IO_wave.export_WAV(filename, audio)
        print(f"Temp file created at: {os.getcwd()}\{filename}")
        # TODO clear up temp file
        from playsound import playsound
        playsound(filename)
        
        try:
            os.remove(filename)
            print("Temp file deleted")
        except:
            print(f"Could not delete temporary file.") #" at: {os.getcwd()}\{filename}")


#### EXPORTED NAMES ##########
'''
Here are the exported functionalities.
TODO add logic to figure out supported libraries (also let user customize),
and direct traffic to the correct classes.
also figure out how to navigate different formats
'''

_io_alternatives = [_IO_wave, _IO_aifc, _IO_SA, _IO_ffmpeg, _IO_playsound, _IO_ffmpeg_python] 
_io_alternatives = {c.name:c for c in _io_alternatives} # as a dictionary for user interaction later

# this will be the eventual interface from Audio,
# and will take care of the logic to decide which libraries to use
def _choose_first_supported(options):
    for o in options:
        if o.is_supported:
            return o
    
    return None

class IO:
    def _choose_defaults():
        play_cls = _choose_first_supported([_IO_SA, _IO_playsound])
        
        load_cls = {"wav": _IO_wave,
                    "aiff": _IO_aifc,
                    "*": _choose_first_supported([_IO_ffmpeg_python, _IO_ffmpeg])}
        
        export_cls = {"wav": _IO_wave,
                      "aiff": _IO_aifc,
                      "*": _choose_first_supported([_IO_ffmpeg_python, _IO_ffmpeg])}
        
        return play_cls, load_cls, export_cls
    
    play_cls, load_cls, export_cls = _choose_defaults()
    
    
    def status(): # print_status? since we may want to receive it programmatically as well
        # prints to user status of default and supported I/O capabilities
        print(" --- Gensound I/O support status ---")
        print(f" playback: {IO.play_cls.name if IO.play_cls else '-'}\n")
        print(" read:")
        
        for fmt in IO.load_cls:
            print(f"\t{fmt}: {IO.load_cls[fmt].name if IO.load_cls[fmt] else '-'}")
        
        print("\n export:")
        
        for fmt in IO.export_cls:
            print(f"\t{fmt}: {IO.export_cls[fmt].name if IO.export_cls[fmt] else '-'}")
        
    
    # TODO let user know what other options are available
    
    def set_io(action, class_name, fmt=None):
        # allows user to switch I/O instruments
        if action == "play":
            IO.play_cls = _io_alternatives[class_name]
        elif action == "load":
            IO.load_cls[fmt if fmt else "*"] = _io_alternatives[class_name]
        elif action == "export":
            IO.export_cls[fmt if fmt else "*"] = _io_alternatives[class_name]
    
    
    def play(*args, **kwargs):
        IO.play_cls.playback(*args, **kwargs)
    
    
    
    def export_WAV(*args, **kwargs):
        IO.export_cls["wav"].export_WAV(*args, **kwargs)
    
    def export_AIFF(*args, **kwargs):
        IO.export_cls["aiff"].export_AIFF(*args, **kwargs)
    
    def export_file(*args, **kwargs):
        IO.export_cls["*"].export_file(*args, **kwargs)
    
    # TODO find the correct place to ensure file exists in the first place
    def WAV_to_Audio(*args, **kwargs):
        return IO.load_cls["wav"].WAV_to_Audio(*args, **kwargs)
    
    def AIFF_to_Audio(*args, **kwargs):
        return IO.load_cls["aiff"].AIFF_to_Audio(*args, **kwargs)
    
    def file_to_Audio(*args, **kwargs):
        return IO.load_cls["*"].file_to_Audio(*args, **kwargs)
    
    
    
    














### for testing purposes; outputs WAV and logs the cade that generated it ####

def export_test(audio, func=None, byte_width=2, max_amplitude=1):
    if not hasattr(audio, "buffer"):
        audio._prepare_buffer(byte_width, max_amplitude)
    
    assert inspect.stack()[1].function == func.__name__, "logging names don't match!!!"
    
    timestamp = time.strftime('%Y-%b-%d_%H%M', time.localtime())
    _IO_wave.export_WAV("../output/export_{timestamp}_{caller.function}.wav".format( 
                   timestamp = timestamp,
                   caller = inspect.stack()[1]),
                audio)
    
    if func is None:
        return
    
    with open("../output/_export_log.txt", "a") as file:
        # TODO make sure not to overwrite
        file.write("++++++ {} ++++++\n------ {} ------\n\n{}\n\n".format(
                                                               func.__name__,
                                                               timestamp,
                                                               inspect.getsource(func)))



