# merged grammar from "testParser.py"
# added Alterations
# PERFS voice et global ->>> OK
# gestion Infoline vsc comment ---->>> OOOOKKKK splited the two parse mechanisms, first loop in order to detect infos and suppress star of line comments

from pyparsing import *
import sys
from AMN_Python_Parser import *
FJ = r"""
#title= Tourdion
#subtitle= Quand je bois du vin clairet
#music author = Anonymous
#parole de chanson à ajouter. Question pour Monsieur Schlick, le langage pour les paroles est-il le même que pour les notes? Ou osef, c'est juste visuel?
#Quand on dit IPN = A4, si on fait un si(B) , ça donne le B5 ou le B4???
#Si on indique la gamme dans les perfs, est-ce que les bémol/ dièses sont mis automatiquement sur la note quand elle est indiquée ou faut quand même les mettre à la main???
#Le ternaire c'est chiant
O global \$ A6 : D \% 104 : 2\

O voixune
|  / EFG AGF / E" FGA / BAG GAF / G' FED / EFG AGF / E' G' F' / E"' D' / E /
:  / B" ABC / B"' B' / >ECBAGF / G" FE' / B" ABC / B'A BF' / E"' D' / E /
:  / B" ABC /***/ B"' B' / >ECBAGF / G" FE' / B" ABC / B'A BF' / E"' D' / E /

O voixdeux \$A4\
|  / B"' B' / E"' E' / D"' E' / E'A / G"' E' / BAB CD' / B' B"' / B /
:  / G"' G' / G"' G' / F"' F' / E"' E' / D"' D' / D"' D' / B' B"' / B /
:  / G"' G' / G"' G' / F"' F' / E"' E' / D"' D' / D"' D' / B' B"' / B /

O voixtrois \$E\
|  / G"' E' / B"' B' / B"' -C' / B"' A' / B"' B' / G"' A' / B'F EF' / E
| >E"' E / D"' D' / E"' E' /***/ B"' B' / B"' B' / B"' A' / B' F"' / E

O voixquatre \$B3\
| E"' E / E"' E / G'>B' A' / E' F"' / E"' E / E"' E / E"' D / E /
| E"' E' / G"' G' / B"' B' / E"' E' / G"' G' / G"' D' / E'B"' / E
"""
Remplie=r"""#title=Remplis ton verre vide
#author=Etienne Daniel
#Chanson à deux voix d'après une chanson à boire de XVIIe s

O global \$ F : D \% 208 : 8\

O voice1
| @"" A / D'D C'B / A" A'A*3 / G'F E'A / F"" F /*4
|  / F'F** E'D / A'A A'A /***/ BCD DEC / D"""
Imagine = r"""

#title = Imagine
#super comment
# music author = John Lennon
#lyrics author=John Lennon
#file author = Clara Sorita

O global \%72:4\ #tempo de 72 bat/ min, 4 temps par mesure
= veR1=[>%Cfa*3,Fa-Bb] veR2=[D_3|eg*3,Deg] veL3=[(<CC)*4] veL2=[(<FC)*4  ] chR1=[(>%CfF)*2,(>%CfE)*2] chR2=[( D>%CfaD , C>%CfaC] chR3=[BG>%(DbG)*2>CeG] chR4=[%Gdf   ] 
= chL=[<F <E ] chL=[<D <C ] chL=[G   ] #ver=> verse right hand / vel => verse left hand/ chr => chorus right hand etc...

O piano \$C4:C\?%\ 
| [Eg-3,Egb.%] veR2 (veR1 veR2)*4 chR1 chR2 chR3 chR4
| (veL1 veL2)*6 chL"""

infosong = r"""
# this is a comment
#title = Supersong # this is a comment
#this is a comment between two infos and it works !
# music author = Clara #this is a comment
#this is a comment
#AMN = 1.0

O global \$C4:C\%72:4\?%\?%            #wahoo

# there's still work to do
O barbasednotation \$C4:C\?% #perfs without closing antislash rocks
| /AAAA/***/BBBB/
: /CGEC/
: /CGEC/

O phrasebasednotation
| /ABC 
: /ABC
"""



class AMNtoLylipond(AMNFileParser):
    def __init__(self,AMNfile):
        AMNFileParser.__init__(self,AMNfile)
        self.translate()
    def translate(self):
        
        #fichier = open(str(self.title)+".ly", "w")
        header = '\header {\n'
        self.__dico_note = {'A': 'a', 'B': 'b', 'C': 'c', 'D': 'd', 'E': 'e', 'F': 'f', 'G': 'g','@':'r'}
        dico_dyn_alteration = {'!': '^', '?': '+', '.': '.', '_': '-'}
        i = 0
        dic = {self.title: "title", self.subtitle: "subtitle", self.musicauthor: "composer",
               self.fileauthor: "arranger", self.lyricsauthor: 'poet'}
        for param in dic:
            if param:
                header += dic[param] + '="' + param + '" \n'
            i += 1
        
        #fichier.write(text)
        #fichier.close()
        score=''
        text = ''
        clef=''
        relative=''
        #global
        if self.Global.perfs.SSIG:
            clef,relative=self.convert_perfs(self.Global.perfs.SSIG)
        
        BPM = self.Global.perfs.BSIG.BPM
        header += 'meter = "' + str(BPM) + '"\n'
        
        for voice in self.Voices:
            newStaff = ''
            merge1 = merge2 = ''
            i=0
            for lines in voice.lines:
                BPB = 0
                for bar in lines.content:
                    BPB = max(BPB, len(bar[0][0]))
                    pulse = 0
                    for elems in bar[0][0]:
                        for elem in elems:
                            pulse += 2 if elem == '"' else 1
                    time = str(pulse) + "/" + str(BPB)
            newStaff += r'\new Staff { \time' + str(time)
            #perfs
            if voice.perfs:
                if voice.perfs.SSIG: clef, relative = self.convert_perfs(voice.perfs.SSIG)
            for lines in voice.lines:
                supplement=''
                for j in range(i):
                    supplement+='a'
                if lines.type == 'split':
                    newStaff += '\\'
                if lines.type == 'merge':
                    newStaff+='}\n '+ '\\new Staff { \\'
                    merge1=r'\new GrandStaff<<\set GrandStaff.instrumentName = #"'+ voice.name+'" '
                    merge2='>>\n'
                text += voice.name + supplement+ '=' + relative + '{' + clef
                newStaff+=voice.name + supplement
                for bar in lines.content:
                    bartext=''
                    for barelem in bar.barcontent:
                        for notes in barelem.Notes:
                            nb = ''
                            if notes[1] == "'":
                                nb = str(pulse*2)
                                bartext += ' ' + self.__dico_note[notes.note] + nb + ' '
                            elif notes[1] == '"':
                                nb= str(pulse*4)
                                bartext += ' ' + self.__dico_note[notes.note] + nb + ' '
                            else:
                                bartext+=' '+ self.__dico_note[notes.note] + ' '
                            if notes.noteRepetition:
                                for i in range(len(notes.noteRepetition)):
                                    bartext+=' '+ self.__dico_note[notes.note] + ' '
                            if notes.noteAlteration:
                                pass
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
            newStaff=merge1+ newStaff+'}\n' +merge2
            score+=newStaff
        score='<<'+score+'>>'
        text+=score
        header += '}\n'
        print(header + text)
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









AMNtoLylipond(Remplie)
