from gensound import WAV, test_wav, Fade, FadeIn, FadeOut, Sine

wav = Sine() # load sample WAV, included with gensound

wav *= FadeIn()
# wav *= FadeOut(curve="polynomial", duration=4e3)
# wav *= Fade()
wav.play()
