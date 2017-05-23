from Midi import *
from AMNtoLylipond import *
import os

file = "demos/gamme.amn"
lily = AMNtoLylipond(file).save()
os.system("start "+lily+".ly")



midi = Midi_Parser(file)
midi.play()
os.system("start "+lily+".pdf")
