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
import copy
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
        
        # GLOBAL PARAMETERS
        self.globalPerfs = {
            "pitch" : "C",
            "octave":5,
            "sign":0,
            "BPM" : 120,
            "dynamicBPM":None,
            "scale" : {'C': 12, 'F': 17, 'A': 21, 'G': 19, 'E': 16, 'D': 14, 'B': 23}
            }
        if self.Global != None:
            if self.Global.perfs:
                self.globalPerfs = self.assignPerfs(self.Global, self.globalPerfs)

        channel = -1
        for i in range(self.nbVoices):
            
            self.localPerfs = copy.copy(self.globalPerfs)       
            self.midi.addTrackName(i, 0, self.Voices[i].name)
            
            #LOCAL PARAMS 
            self.localPerfs = self.assignPerfs(self.Voices[i], self.localPerfs)
            print(self.localPerfs["BPM"])
            if self.Voices[i].name in voices.keys():
                timecounter = voices[self.Voices[i].name]["endtracktime"]
            else:
                voices[self.Voices[i].name]={}
                timecounter = 0
                
                if self.Voices[i].name in self.instrus:
                    voices[self.Voices[i].name]["instru"] = self.Voices[i].name
                else :
                    voices[self.Voices[i].name]["instru"] = "piano"
                channel +=1
                voices[self.Voices[i].name]["channel"] = channel
                self.midi.addProgramChange(i, voices[self.Voices[i].name]["channel"], 0, self.instrus[voices[self.Voices[i].name]["instru"]])
                

                
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
                        print("track",i)
                        print("BPM",self.localPerfs["BPM"])
                        self.midi.addTempo(i, timecounter, copy.copy(self.localPerfs["BPM"]))
                        timels = []
                        
                        #bar repetition + bar alt TODO
                        barrepetition = 1
                        if bar.barRep :
                            if bar.repsuite:
                                barrepetition+=len(bar.repsuite)
                            elif bar.repfactor:
                                barrepetition=int(bar.repfactor)

                        for timel in bar.barcontent:
                            #durée d'un timel en beats
                            timelpulses = 0
                            notes =[]

                            #if group stuff repetitions ou alts
                            for note in timel.Notes:
                                duration = 1
                                #note alterations
                                # dynamic alteration ? to MIDI ? :(
                                if note.note in "A,B,C,D,E,F,G,@".split(","):
                                    if note.note == "@":
                                        pitch = -1
                                    else :
                                        pitch = self.getMidiPitch(note.note, self.localPerfs["octave"], self.localPerfs["sign"], self.localPerfs["scale"])

                                        # Note alteration
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

                                #note repetition 
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
                            
                        for k in range(barrepetition):
                            for note in allnotes:
                                if note["pitch"] != -1 :
                                    self.midi.addNote(
                                        i,voices[self.Voices[i].name]["channel"],note["pitch"],
                                        timecounter,
                                        note["duration"]/barpulses,
                                        note["volume"])
                                timecounter += note["duration"]/barpulses
                            
                    if line.type == "split":
                        lastsplitendtime = timecounter
                        voices[self.Voices[i].name]["endtracktime"] = lastsplitendtime

    @property
    def globalMidiPitch(self):
        return self.getMidiPitch(note=self.globalpitch,
                            octave=self.globaloctave,
                            sign=self.globalsign,
                            gamme=self.globalscale
                            )

    @globalMidiPitch.setter
    def globalMidiPitch(self,newmidi):
        self.globalpitch, self.globaloctave, self.globalsign = self.getPitchOctave(newmidi)

    @property
    def localMidiPitch(self):
        return self.getMidiPitch(note=self.localpitch,
                            octave=self.localoctave,
                            sign=self.localsign,
                            gamme=self.localscale
                            )

    @globalMidiPitch.setter
    def localMidiPitch(self,newmidi):
        self.localpitch, self.localoctave, self.localsign = self.getPitchOctave(newmidi)

    def getPitchOctave(self,newmidi): #afaire mais pas necessaire
        octave = newmidi//12
        pitch = "C"
        sign = 0
        return pitch, octave, sign
    
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
    
    def getMidiPitch(self, note="C", octave=5, sign=0, gamme=None):
        if gamme:
            gammebase = gamme
        else :
            gammebase = self.getGamme()
        pitch = (gammebase[note]+octave*12)+sign
        return pitch

    def getGamme(self, scaleNote = "C", scaleSign = 0, customInt=None):
        intM = [2,2,1,2,2,2,1]
        intm = [2,1,2,2,1,3,1]
                    
        if customInt:
            intervalles = customInt
        elif scaleNote in ["A","B","C","D","E","F","G"]:
            intervalles = intM
        elif scaleNote in ["a","b","c","d","e","f","g"]:
            intervalles = intm
            
        scales = ["C","D","E","F","G","A","B"]
        gamnote = scaleNote.upper()
        base = sum(intM[0:scales.index(gamnote)])
        base += scaleSign
        order = ["C","D","E","F","G","A","B"]
        order = order[order.index(gamnote)+1:]+order[0:order.index(gamnote)]
        gamme ={}
        gamme[gamnote] = base
        i=0
        for pitch in order:
            base += intervalles[i]
            gamme[pitch] = base
            i +=1
        return gamme
    
    def assignPerfs(self, this, outdico):
        if this.perfs :
            if this.perfs.SSIG:
                if this.perfs.MPN:
                    outdico["midiPitch"] = int(this.MPN)
                elif this.perfs.SSIG.IPN:
                    s = {"-" : -1,"+":1}
                    outdico["sign"] = 0
                    if this.perfs.SSIG.IPN.sign in s.keys():
                        outdico["sign"] = s[this.SSIG.IPN.sign]
                    outdico["pitch"] = this.perfs.SSIG.IPN.pitch
                    if this.perfs.SSIG.IPN.octave:
                        mod = {"<":-1,"<<":-2,">":1,">>":2}
                        if this.perfs.SSIG.IPN.octave in mod.keys():
                            outdico["octave"] += mod[this.perfs.SSIG.IPN.octave]
                        elif this.perfs.SSIG.IPN.octave in ["0","1","2","3","4","5","6","7","8","9"]:
                            outdico["octave"] = int(this.perfs.SSIG.IPN.octave)

                    scalenote = "C"
                    scalesign = 0
                    if this.perfs.SSIG.scalekey:
                        scalenote = this.perfs.SSIG.scalekey.note
                        if this.perfs.SSIG.scalekey.sign:
                            scalesign = s[this.perfs.SSIG.scalekey.sign]  
                    outdico["scale"] = self.getGamme(scaleNote = scalenote, scaleSign = scalesign)
                    
            if this.perfs.BSIG:
                outdico["BPM"] = int(this.perfs.BSIG.BPM)
                if this.perfs.BSIG.dynamic:
                    outdico["dynamicBPM"] = int(this.perfs.BSIG.dynamic)
        return outdico
    
    def save(self):
        if self.title:
            title = self.title
        else :
            title = "out"
        filename = title+".midi"
        with open(filename, 'wb') as output_file:
            self.midi.writeFile(output_file) 
        print("saved as : "+filename)
        return filename
        
    def play(self):
        filename = self.save()
        with open(filename, 'wb') as output_file:
            self.midi.writeFile(output_file) 
        os.system("start "+filename)
Midi_Parser("demos/gamme.amn").play()
