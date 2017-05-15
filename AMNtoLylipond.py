# merged grammar from "testParser.py"
# added Alterations
# PERFS voice et global ->>> OK
# gestion Infoline vsc comment ---->>> OOOOKKKK splited the two parse mechanisms, first loop in order to detect infos and suppress star of line comments

from pyparsing import *
import sys
from AMN_Python_Parser import *
FJ = r"""
#title= Les lapins sont en vacances
#music author = Dudulle
O piano \$ B4:C\%120:4\
| / .Ce,.Ce ,.Df,.Df / .Eg,.Eg ,_Eg / .Df,.Df ,.Eg,.Eg/ .Fa,.Fa ,_Fa/.>%Gb,.Fa ,.Eg/ .Eg,.Df ,.Ce /
| /.Eg,.Df,.Ce,.Ce / .Bd,.Bd, _C/
: /C >G / C /D A / D / >G G / AB C / G C / G C
"""

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
| /AAAA/***
| /BBBB/
: /CGEC/

O phrasebasednotation
| /ABC 
"""



class AMNtoLylipond(AMNFileParser):
    def __init__(self,AMNfile):
        AMNFileParser.__init__(self,AMNfile)
        self.translate()
    def translate(self):
        
        fichier = open(str(self.title)+".ly", "w")
        text = '\header {\n'
        dico_note = {'A': 'a', 'B': 'b', 'C': 'c', 'D': 'd', 'E': 'e', 'F': 'f', 'G': 'g'}
        dico_dyn_alteration = {'!': '^', '?': '+', '.': '.', '_': '-'}
        i = 0
        dic = {self.title: "title", self.subtitle: "subtitle", self.musicauthor: "composer",
               self.fileauthor: "arranger", self.lyricsauthor: 'poet'}
        for param in dic:
            if param:
                text += dic[param] + '="' + param + '" \n'
            i += 1
        text += '}\n'
        fichier.write(text)
        fichier.close()
        score=''
        for voice in self.Voices:
            merge = ''
            i=0
            score+=r'\new Staff { '
            for lines in voice.lines:
                supplement=''
                for j in range(i):
                    supplement+='a'

                if lines.type == 'split':
                    score += '\\'
                if lines.type == 'merge':
                    score='<< '+score+'}\n '+ '\\new Staff { \\'
                    merge='>>\n'
                text += voice.name + supplement+ '='
                for bar in lines.content:
                    if bar.barRep:
                        score += 'set countPercentRepeats = ##t \n' + r'\repeat percent ' + str(len(bar.barRep) + 1) + '{ \\' + voice.name + supplement + '}'
                    else:
                        score+= voice.name + supplement + ' '
                    bartext='{'
                    for barelem in bar.barcontent:
                        for notes in barelem.Notes:
                            bartext+=' '+dico_note[notes.note] + ' '
                            if notes.noteRepetition:
                                for i in range(len(notes.noteRepetition)):
                                    bartext+=' '+dico_note[notes.note] + ' '
                            if notes.noteAlteration:
                                pass

                    text+=bartext + '} '
                                 #donne un fichier bartext qui donne le contenu de la bar traduit
                    i += 1
                score+='\n'
                text += '\n'
            score+='}\n' +merge
        text+=score
        print(text)










AMNtoLylipond(infosong)
