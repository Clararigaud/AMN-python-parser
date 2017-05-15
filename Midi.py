from midiutil import MIDIFile
from AMN_Python_Parser import *

test = r"""
O piano
| [CDEC][CDEC] [EF G][EF G] [G"A GF E C][G"A GF E C] [C<G C][C<G C] #frere jacques bitches
"""
def getFrequency(note):
    pitchs = {"A":21,
             "B":23,
             "C":24,
             "D":26,
             "E":28,
             "F":29,
             "G":31
             }
    hauteur = 2
    elevation = 0
    reduction = 0
    pitch = pitchs[note.note]+hauteur*12+elevation-reduction
    return pitch

parsed = AMNFileParser(test)
nbvoices = parsed.nbVoices
MyMIDI = MIDIFile(nbvoices, file_format=1, adjust_origin=False)
for i in range(nbvoices):
    timecounter = 0
    beatperbars = 4
    beatperminute = 60
    localperfs = parsed.Voices[i].perfs
    splitcount = 0
    for line in parsed.Voices[i].lines :   
        if line.type == "split":
            lastsplittime = timecounter
            for bar in line.content:
                barpulses = 0
                allnotes = []
                MyMIDI.addTempo(i, 0, beatperminute)
                timels = []
                for timel in bar.barcontent:
                     #durée d'un timel en beats
                    timelpulses = 0
                    notes =[]
                    for note in timel.Notes:
                        duration = 1
                        pitch = getFrequency(note)
                        for timAlt in note.timeAlteration:
                            if timAlt == "'":
                                duration+=1
                            elif timAlt == "\"":
                                duration+=2
                        notes+=[{"pitch":pitch, "duration":duration,"volume":100}]
                        timelpulses +=duration
                    for note in notes:
                        note["duration"]= note["duration"]/timelpulses
                        barpulses+=note["duration"]
                    allnotes+=notes
                for note in allnotes:
                    MyMIDI.addNote(i,0,note["pitch"],timecounter,note["duration"]/barpulses,note["volume"])
                    timecounter += note["duration"]/barpulses
                    

with open("lol.midi", 'wb') as output_file:
    MyMIDI.writeFile(output_file)
print("ok")
