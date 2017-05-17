#|------------------------79 CHARACTERRRRS----:°----:o--------:0-----------:D--
#========================C'est=de=la=torture=!=================================
try:
    from midiutil import MIDIFile
except ImportError:
    print("\nmidiutil n'est pas installé")
    try:
        import pip
        print("\nInstallation du module MIDIUtil")
        pip.main(['install', "MIDIUtil"])
        from midiutil import MIDIFile
    except:
        print("failed")

from AMN_Python_Parser import *
import os
test = r"""
O global \$C5\%80

O atmosphere
| [CDEC][CDEC] [EF G][EF G] [G"A GF E C][G"A GF E C] [C<G C][C<G C]
#frere jacques bitches
#: [EFGE][EFGE] [GA B][GA B] [B"C BH G E][B"C BH G E] [E<B E][E<B E]
#merge line synchro avec split line

O ocarina
| /++65%!!!5C*/C>>C
"""


          
class Midi_Parser(AMNFileParser):
    def __init__(self,file):
        AMNFileParser.__init__(self,file)
        self.midi = MIDIFile(self.nbVoices, file_format=1, adjust_origin=False)

        #https://fr.wikipedia.org/wiki/General_MIDI
        self.instrus ={"piano":3,
                       "harpe": 46,
                       "violon": 40,
                       "violoncelle": 42,
                       "piccolo":72,
                       "ocarina":79,
                       "sifflet":78,
                       "bouteille":76,
                       "choeurs":91,
                       "atmosphere":99,
                       "gobelins":101,
                       "echos":102,
                       "espace": 103,
                       "cornemuse": 109,
                       "glokenspiel":9}
        voices = {}
        self.globalpitch = 72 #default C5->72
        self.globalBPM = 120
        self.dynamicBPM = None
        self.globalBeatPerBar = 4 #dunno what to do with this information       

        if self.Global != None:
            if self.Global.perfs:
                pitch,BPM,dBPM=self.getPerfs(
                    self.Global.perfs
                    )
                if pitch :self.globalpitch = pitch
                if BPM : self.globalBPM = BPM
                if dBPM : self.dynamicBPM = dBPM
        for i in range(self.nbVoices):
            localBPM = self.globalBPM
            localdynamicBPM = self.dynamicBPM
            localpitch = self.globalpitch
            if self.Voices[i].perfs:
                pitch,BPM,dBPM=self.getPerfs(
                    self.Voices[i].perfs
                    )
                if pitch :localpitch = pitch
                if BPM : localBPM = BPM
                if dBPM : localdynamicBPM = dBPM

            if self.Voices[i].name in voices.keys():
                timecounter = voices[self.Voices[i].name]["endtracktime"]
            else:
                voices[self.Voices[i].name]={}
                timecounter = 0
                channel = 0
                time    = 0 # Eight beats into the composition
                program = self.instrus[self.Voices[i].name]# instrumeeent
                self.midi.addProgramChange(i, channel, time, program)


                
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
                        self.midi.addTempo(i, 0, localBPM)
                        timels = []

                        #bar repetition + bar alt TODO
                        for timel in bar.barcontent:
                            #durée d'un timel en beats
                            timelpulses = 0
                            notes =[]

                            #if group stuff repetitions ou alts
                            for note in timel.Notes:
                                duration = 1
                                #note alterations
                                # dynamic alteration ? to MIDI ? :(
                                pitch = self.getMidiPitch(note.note)
                                if note.pitch :
                                    char = note.pitch.alt[0]
                                    shifts = {"+":1,
                                              "-":-1,
                                              ">":12,
                                              "<":-12
                                              }
                                    if char in shifts.keys():
                                        result = 0
                                        coeff = shifts[char]
                                        s= len(note.pitch.alt)

                                        if len(note.pitch.strength) > 0:
                                            s += int(note.pitch.strength[0])
                                            if len(note.pitch.strength)==2:
                                                if note.pitch.strength[1] == "%":
                                                    s+= 0.5
                                        pitch += int(coeff*s) # int ici car pas trouvé comment faire des quarts de tons (option ChangeTuning de la lib)
                                    else :
                                        print(char+ " is not implemented yet at line %s"%line.fileLine)

                                #note repetition works
                                repetition = 1
                                if note.noteRepetition :
                                    if note.repsuite:
                                        repetition+=len(note.repsuite)
                                    elif note.repfactor:
                                        repetition=int(note.repfactor)
                                
                                
                                for timAlt in note.timeAlteration:
                                    if timAlt == "'":
                                        duration+=1
                                    elif timAlt == "\"":
                                        duration+=2
                                        
                                
                                for k in range(repetition):
                                    notes+=[
                                        {"pitch":pitch,
                                         "duration":duration,
                                         "volume":100}
                                        ]
                                    timelpulses +=duration
                                
                            for note in notes:
                                note["duration"]= note["duration"]/timelpulses
                                barpulses+=note["duration"]
                            allnotes+=notes
                        for note in allnotes:
                            self.midi.addNote(
                                i,0,note["pitch"],
                                timecounter,
                                note["duration"]/barpulses,
                                note["volume"])
                            timecounter += note["duration"]/barpulses
                    if line.type == "split":
                        lastsplitendtime = timecounter
                        voices[self.Voices[i].name]["endtracktime"] = lastsplitendtime

    def getPerfs(self, perfs):
        pitch=None
        BPM= None
        dynamic = None
        if perfs.SSIG:
            if perfs.MPN:
                pitch = int(self.Global.MPN)
            elif perfs.SSIG.IPN:
                s = {"-" : -1,"+":1}
                sign = 0
                if perfs.SSIG.IPN.sign in s.keys():
                    sign = s[perfs.SSIG.IPN.sign]
                pitch = perfs.SSIG.IPN.pitch
                octave = int(perfs.SSIG.IPN.octave)
                pitch = self.getMidiPitch(pitch, octave, sign)

        if perfs.BSIG:
            BPM = int(perfs.BSIG.BPM)
            if perfs.BSIG.dynamic:
                dynamic = int(perfs.BSIG.dynamic)
                
        return pitch,BPM,dynamic
    
    def getMidiPitch(self, note="C", octave=5, sign=0):
        pitchs = {"A":21,
                 "B":23,
                 "C":12,
                 "D":14,
                 "E":16,
                 "F":17,
                 "G":19
                 }

        pitch = (pitchs[note]+octave*12)+sign
        return pitch

parsed = Midi_Parser(test)
print(parsed)
filename = "lol.midi"
os.system("stop "+filename)
with open(filename, 'wb') as output_file:
    parsed.midi.writeFile(output_file)
os.system("start "+filename)
print("ok")
