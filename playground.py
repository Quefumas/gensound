from gensound import WAV, test_wav, FadeIn

wav = WAV(test_wav) # load sample WAV, included with gensound
wav *= FadeIn(duration=5000)
wav.play()
