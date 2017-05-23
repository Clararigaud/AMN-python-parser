from Midi import *
from AMNtoLylipond import *
import os

file = "demos/frerejacques.amn"
lily = AMNtoLylipond(file).save()
os.system("start "+lily)


midi = Midi_Parser(file)
midi.play()
