# merged grammar from "testParser.py"
# added Alterations
# PERFS voice et global ->>> OK
# gestion Infoline vsc comment ---->>> OOOOKKKK splited the two parse mechanisms, first loop in order to detect infos and suppress star of line comments

from pyparsing import *
import sys
from AMN_Python_Parser import *

class AMNtoLylipond(AMNFileParser):
    def __init__(self,AMNfile):
        AMNFileParser.__init__(self,AMNfile)
        self.translate()
    def translate(self):
        header = '\header {\n'
        self.__dico_note = {'A': 'a', 'B': 'b', 'C': 'c', 'D': 'd', 'E': 'e', 'F': 'f', 'G': 'g','@':'r'}
        self.__dico_pitch_alt={'+':'es','-':'es','>':"'",'<':',','~':'\glissando '}
        self.__dico_dyn_alt = {'!': '^', '?': '+', '.': '.', '_': '-'}
        i = 0
        dic = {self.title: "title", self.subtitle: "subtitle", self.musicauthor: "composer",
               self.fileauthor: "arranger", self.lyricsauthor: 'poet'}
        for param in dic:
            if param:
                header += dic[param] + '="' + param + '" \n'
            i += 1
        
        score=''
        text = ''
        clef=''
        relative=''
        #global
        if self.Global:
            if self.Global.perfs.SSIG:
                clef,relative=self.convert_perfs(self.Global.perfs.SSIG)
                BPM = self.Global.perfs.BSIG.BPM
            else:
                BPM=4
        else:
            BPM = 4
        header += 'meter = "' + str(BPM) + '"\n'
        
        for voice in self.Voices:
            newStaff = ''
            merge1 = merge2 = ''
            i=0
            pulse = 4
            time=4
            for lines in voice.lines:
                BPB = 4
                max_pulse = 0
                for bar in lines.content:
                    self.__nbelem = 0
                    BPB = max(BPB, len(bar[0][0]))
                    pulse = 3
                    for elems in bar[0][0]:
                        for elem in elems:
                            pulse += 2 if elem == '"' else 1
                            max_pulse = max(pulse,max_pulse)
                    pulse = 4
                    time = str(pulse) + "/" + str(BPB)
                            
            newStaff += r'\new Staff { \time' + str(time)
            #perfs
            if voice.perfs:
                if voice.perfs.SSIG: clef, relative = self.convert_perfs(voice.perfs.SSIG)
            valt=''
            if voice.volumealteration:
                for volumealteration in voice.volumealteration:
                    #forte
                    if volumealteration.factorforte :
                        if int(volumealteration.factorforte)>=5 :
                            valt+=r'\fffff'
                        else:
                            valt += '\\'
                            n = int(volumealteration.factorforte)
                            for i in range(n):
                                valt+='f'
                    elif volumealteration.suiteforte:
                        if len(volumealteration.suiteforte)>=5:
                            valt += r'\fffff'
                        else:
                            valt+='\\'
                            n=len(volumealteration.suiteforte)
                            for i in range(n):
                                valt+='f'
                    #piano
                    if volumealteration.factorpiano:
                        if int(volumealteration.factorpiano)>=5 :
                            valt+=r'\ppppp'
                        else:
                            valt += '\\'
                            n = int(volumealteration.factorpiano)
                            for i in range(n):
                                valt+='p'
                    elif volumealteration.suitepiano:
                        if len(volumealteration.suitepiano)>=5:
                            valt += r'\ppppp'
                        else:
                            valt+='\\'
                            n=len(volumealteration.suitepiano)
                            for i in range(n):
                                valt+='p'


            for lines in voice.lines:
                supplement=''
                for j in range(i):
                    supplement+='a'
                #Merge ou split
                if lines.type == 'split':
                    newStaff += '\\'
                if lines.type == 'merge':
                    newStaff+='}\n '+ '\\new Staff { \\'
                    merge1=r'\new GrandStaff<<\set GrandStaff.instrumentName = #"'+ voice.name+'" '
                    merge2='>>\n'
                if lines.types=='data':
                    clef, relative = self.convert_perfs(voice.perfs.SSIG)
                #Ajout de la hauteur des perfs locales ou globales
                text += voice.name + supplement+ '=' + relative + '{' + clef
                newStaff+=voice.name + supplement
                #Parcours des mesures
                for bar in lines.content:
                    bartext=''
                    #Parcours des élements dans les mesures
                    for barelem in bar.barcontent:
                        rythme = ''
                        #Notes
                        for notes in barelem.Notes:
                            nb = ''
                            var=0
                            quart=0
                            self.__long = False
                            alteration=''
                            newNote=''
                            #Alterations
                            if notes.noteAlteration:
                                if notes.noteAlteration.pitch:
                                    if notes.pitch.strength:
                                        if len(notes.pitch.strength) == 2:
                                            if notes.pitch.strength[1] == "%":
                                                quart += 0.5
                                        if notes.noteAlteration.pitch.alt[0] in ('<','-'):
                                            var -= int(notes.pitch.strength[0])-1
                                        elif notes.noteAlteration.pitch.alt[0] in ('>','+'):
                                            var += int(notes.pitch.strength[0])-1
                                    #Pitch
                                    for alt in notes.noteAlteration.pitch.alt:
                                        if alt in ('+','-'):
                                            if alt=='+':var+=1
                                            if alt=='-': var-=1
                                            newNote = self.varPitch(self.__dico_note[notes.note], var, quart)
                                        elif alt in ('<','>'):
                                            if alt=='>':
                                                var+=1
                                                alteration+= self.__dico_pitch_alt[alt]
                                                if quart != 0:
                                                    newNote = self.varPitch(self.__dico_note[notes.note], 12, 0)
                                                for i in range(var-1):
                                                    alteration += self.__dico_pitch_alt[alt]
                                            elif alt=='<':
                                                var -= 1
                                                alteration +=  self.__dico_pitch_alt[alt]
                                                if quart != 0:
                                                    newNote = self.varPitch(self.__dico_note[notes.note], -12, 0)
                                                for i in range(-var-1):
                                                    alteration += self.__dico_pitch_alt[alt]

                                        else:
                                            alteration += self.__dico_pitch_alt[alt]
                                # Dynamic #Tellement moins chiaaaaaant
                                if notes.noteAlteration.dynamic:
                                    for alt in notes.noteAlteration.dynamic.alt:
                                        alteration+= '-'+self.__dico_dyn_alt[alt]

                            if newNote=='':newNote=self.__dico_note[notes.note]
                            #Rythme + notes
                            rythme = self.nbRythme(BPB,barelem,notes,bar)
                            if rythme == None:
                                rythme = ''

                            bartext += ' ' + self.__dico_note[notes.note] + str(rythme) + ' '
                            
                            valt=''
                        #Répétition de notes
                        if notes.noteRepetition:
                            for i in range(len(notes.noteRepetition)):
                                bartext+=' '+ newNote + ' '
                    #Répétitions de mesures
                    if bar.barRep:
                        if bar.repfactor:
                            nb_rep=int(bar.repfactor)
                        else:
                            nb_rep=len(bar.barRep)+1
                        text += r'\repeat percent' + str(nb_rep)+'{'+bartext + '} '
                    else:
                        text += bartext
                    i += 1
                text += '} \n'
            #The END
            newStaff=merge1+ newStaff+'}\n' +merge2
            score+=newStaff
        score='<<'+score+'>>'
        text+=score
        header += '}\n'
        self.file = header + text
    def save(self):
        if self.title:
            title = self.title.replace(" ", "")
        else :
            title = "out"
        filename = title+".ly"
        fichier = open(title+".ly", "w")
        fichier.write(self.file)
        fichier.close()
        return title+".pdf"
    def convert_perfs(self,ssig):
        clef=''
        relative=''
        hauteur = 5
        if ssig.IPN:
            relative = self.__dico_note[ssig.IPN.pitch]
            if ssig.IPN.octave:
                hauteur=int(ssig.IPN.octave)

        if ssig.MPN:
            list = ['C', 'C', 'D', 'D', 'E', 'F', 'F', 'G', 'G', 'A', 'A', 'B']
            octave = int(ssig.MPN) // 12 - 1
            pitch = list[int(ssig.MPN) % 12]
            relative = self.__dico_note[pitch]
            hauteur=octave

        if hauteur < 5:
            clef = '\clef bass'
            for i in range(hauteur, 4):
                relative += ','
        else:
            for i in reversed(range(4,hauteur)):
                relative+="'"
        relative = r'\relative '+ relative
        return clef, relative
    def varPitch(self,note,var,quart):
        dicoplus={'a':'b','b':'c','c':'d','d':'e','e':'f','f':'g','g':'a'}
        dicomoins={'a':'g','g':'f','f':'e','e':'d','d':'c','c':'b','b':'a'}
        newNote=''
        var2=var//2
        reste=var%2
        octave=''
        if var2>0:
            if var2 > 7:
                for i in range(var2//7):
                    octave+="'"
                for j in range(var2%7):
                    note=dicoplus[note]
            else:
                for i in range(var2):
                    note = dicoplus[note]
            newNote = note + newNote
            if reste !=0:
                newNote += 'is'
            if quart == 0.5:
                newNote+='ih'
        elif var2<0:
            if var2 <-7:
                for i in range(-var2//7):
                    octave+=','
                for j in range(-var2%7):
                    note=dicomoins[note]
            else:
                for i in range(-var2):
                    note=dicomoins[note]
            newNote = note + newNote
            if reste != 0:
                newNote += 'es'
            if quart == 0.5:
                newNote+='eh'
        else:
            newNote = note + newNote
        newNote+=octave
        return newNote
    
    def nbRythme(self,BPB,bar,note,mesure):
        
        if len(bar) == BPB:
            return int(BPB)
        else:
            if len(note) > 1 :
                for elem in note:
                    if note[1] =='"':
                        self.__long = True
                        return str(BPB*2) +'.'
                    elif elem in ['A','B','C','D','E','F','G']:
                        if elem in bar[self.__nbelem]:
                            rythme = len(mesure[0][0])*(len(bar)-1)
                            if len(bar[self.__nbelem]) < self.__nbelem:
                                self.__nbelem += 1
                            else:
                                self.__nbelem = 0
                            return int(rythme)


            elif note[0] in bar[self.__nbelem]:
                nbbar = len(bar)
                if '"' in bar:
                    if self.__long == True:
                        self.__long = False
                        return BPB * 2
                    else:
                        return BPB * 4
                for a in bar:
                    if a not in ['A','B','C','D','E','F','G']:
                        nbbar -=1
                rythme = len(mesure[0][0])*nbbar
                if len(bar[self.__nbelem]) < self.__nbelem:
                    self.__nbelem = 0
                else:
                    if self.__nbelem+1 >= len(bar[self.__nbelem]):
                        self.__nbelem = 0
                    else:
                        self.__nbelem += 1
                return int(rythme)
            else:
                nbbar = len(bar)
                for a in bar:
                    if a not in ['A','B','C','D','E','F','G']:
                        nbbar -=1
                if bar[1] == '"':
                    nbbar *= 2
                rythme = len(mesure[0][0])*nbbar
                return int(rythme)





AMNtoLylipond("demos/frerejacques.amn")







AMNtoLylipond("demos/frerejacques.amn")
