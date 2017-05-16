from midiutil import MIDIFile
from AMN_Python_Parser import *
import os
test = r"""
O piano
| [CDEC][CDEC] [EF G][EF G] [G"A GF E C][G"A GF E C] [C<G C][C<G C] #frere jacques bitches
: [EFGE][EFGE] [GA B][GA B] [B"C BH G E][B"C BH G E] [E<B E][E<B E]

O flute
| [DEFD]

O piano
| [CCCD][E' D']
: [EEEF][G' F']
"""
class Midi_Parser(AMNFileParser):
    def __init__(self,file):
        AMNFileParser.__init__(self,file)
        self.midi = MIDIFile(self.nbVoices, file_format=1, adjust_origin=False)
        voices = {}
        #if global -> add global params
        for i in range(self.nbVoices):
            if self.Voices[i].name in voices.keys():
                timecounter = voices[self.Voices[i].name]["endtracktime"]
            else:
                voices[self.Voices[i].name]={}
                timecounter = 0
            #local params    
            beatperbars = 4
            beatperminute = 60
            localperfs = self.Voices[i].perfs
            splitcount = 0
            print("voice perfs",localperfs)
            
            for line in self.Voices[i].lines :
                if line.type == "data":
                    pass #change local variables
                elif line.type == "split" or "merge": 
                    if line.type == "split":
                        lastsplitstarttime = timecounter
                    elif line.type == "merge":
                        timecounter = lastsplitstarttime
                    for bar in line.content:
                        barpulses = 0
                        allnotes = []
                        self.midi.addTempo(i, 0, beatperminute)
                        timels = []
                        for timel in bar.barcontent:
                            #durée d'un timel en beats
                            timelpulses = 0
                            notes =[]
                            for note in timel.Notes:
                                duration = 1
                                pitch = self.getFrequency(note)
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
                            self.midi.addNote(i,0,note["pitch"],timecounter,note["duration"]/barpulses,note["volume"])
                            timecounter += note["duration"]/barpulses
                    if line.type == "split":
                        lastsplitendtime = timecounter
                        voices[self.Voices[i].name]["endtracktime"] = lastsplitendtime

                        
    def getFrequency(self, note):
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

parsed = Midi_Parser(test)
print(parsed)
filename = "lol.midi"
with open(filename, 'wb') as output_file:
    parsed.midi.writeFile(output_file)
os.system("start "+filename)
print("ok")
