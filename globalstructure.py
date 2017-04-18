#merged grammar from "testParser.py"
#added Alterations
# PERFS voice et global ->>> OK
# gestion Infoline vsc comment ---->>> OOOOKKKK splited the two parse mechanisms, first loop in order to detect infos and suppress star of line comments

from pyparsing import *
import sys
FJ = r"""
# AMN = 1.0
# title = Frère Jacques
# ceci est un commentaire
O kazoo \$C6 # bar-based notation
|  CDEC /*/ EF G / * / G"A GF E C / * / C<G C  / *

O  piano \$C6 # phrase-based notation
|  [CDEC]* [EF G]* [G"A GF E C]* [C<G C]*

O  flute \$C6 # add dynamics alteration
|  :[CD_EC]* :[EF G]* [!G"A GF _E _C]* ![C<G C  / C<G C0]

O  flute \$C6 # add chords
|  :[CD_EC]* :[EF G]* [!G"A GF _E _C]* ![C<G C  / C<G C0]
<   [CM]*     [Em.]*  [Dm.     CM.]*    [CM. CM / CM  C.M]

O  vox \$C5 # add lyrics 
|  [C  ,D  ,E   ,C    ]* [E       ,F   ;G    ]*
>  [Frè,re ,Ja  ,cques]* [dor     ,mez ;vous?]*
>  [Are,you,slee,ping?]* [Bro     ,ther;John ]*
>  [Bru,der,Ja  ,kob  ]* [Schläfst,du  ;noch?]*

|  [G" ,A   ;G    ,F  ;E   ;C   ]* [C   ,<G  ;C   ]*
>  [So ,nnez;les  ,ma ;ti  ;nes ]* [Ding,Dang;Dong]*
>  [Mor,ning;bells,are;ring;ing ]* [Ding,Dang;Dong]*
>  [Hörst,du;nicht,die;Gloc;ken?]* [Ding,Dang;Dong]*"""

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
= toBeContinued #todo
= toBeContinued #todo

# there's still work to do
O barbasednotation \$C4:C\?% #perfs without closing antislash rocks
= toBeContinued
| /!/C>D*EC /*******/EF\>\ G /*59
: /CGEC/

O phrasebasednotation
| /ABC 
"""

# le caractère antislash fait des conflits (car c'est le char qui permet d'echapper dans les strings python)
#donc il faut bien mettre un "r" pour "raw" avant

class AMNFileParser(object):
    def __init__(self,AMNFile):

        self.__file = AMNFile #make checkups
        self.__AMN = None
        self.__title = None
        self.__subtitle = None
        self.__merge = None
        self.__musicauthor = None
        self.__lyricsauthor = None
        self.__fileauthor = None
        self.__Global = None
        self.__Voices = {}
        parsed = self.parseFile()
        
        for info in parsed["infos"] :
            setattr(self,info["keyWord"].replace(" ", ""),info["value"]) #Makes it an attribute
     
        for voice in parsed["voices"]:
            if voice["name"] == "global":
                self.__Global = voice
            elif voice["name"] in self.__Voices.keys() :
                self.__Voices[voice["name"]]+=[voice]
            else :
                self.__Voices[voice["name"]]=[voice]
            
    def __str__(self):
        s = """\n--------FILE INFOS------------
AMN version: {0.AMN}
Title: {0.title}
subtitle: {0.subtitle}
Music Author: {0.musicauthor}
Lyrics Author:{0.lyricsauthor}
File Author:{0.fileauthor}
File to merge: {0.merge}
Nb Voices:{0.nbVoices}""".format(self)

        if self.__Global:
            s+="""
Global : 
    Perfs: {0.Global[perfs]}
    Datas : {0.Global[lines]}
    """.format(self)

        for instru in self.__Voices.items():
            s+= "\n"+instru[0]
            
        return s
    
    def parseFile(self):
        """ Return a tuple (list, PyParsing.ParseResult object) """
        com = pythonStyleComment
        #BSIG
        BPM = OneOrMore(Word(nums))
        dynamicBPM = BPM + "~" + BPM
        INT = Word(nums)
        PATTERN = Optional(oneOf(":  ")) + INT 
        SBEAT = Word(nums)
        CBEAT = Suppress(Literal('[')) + (PATTERN | (Literal('/')+PATTERN) | (Literal(' ')+PATTERN) ) + Suppress(Literal(']'))
        BSIG= (Suppress(Literal('%')) + Optional(BPM| dynamicBPM) + Optional(Literal(':') + (SBEAT | CBEAT)))

        #SSIG a l'air OK
        Octave = oneOf('<< < > >>')|Word(srange("[0-9]"),exact=1)
        Pitch = Word(srange('[A-G]'),exact=1)
        Sign = oneOf('+ -')
        Key = Optional(Sign) + (Word(srange("[A-G]"),exact=1)("MAJOR") | Word(srange("[a-g]"),exact=1)("MINOR"))
        Fifth = '0' | Sign + Word(srange("[1-7]"),exact=1)
        Degree = Word(alphas)
        SSCALE = Key | Fifth
        Lower = OneOrMore("-") + Optional(Optional(Word(nums) | "%"))
        Raise = OneOrMore("+") + Optional(Optional(Word(nums) | "%"))
        Freq = "="+ Word(nums) + Optional(oneOf("' Hz"))
        Tone = Word(alphas)
        MPN = Word(nums) #entre 0 et 127 
        IPN = Optional(Sign) + Pitch + Optional(Octave)
        EOS = MPN("MPN") | IPN("IPN")
        Step = Tone + (Freq | Raise) + Lower + Raise + Degree
        CSCALE = Literal('[') + Step + Literal('$]')
        SSIG = (Suppress(Literal('$')) + EOS("EOS") + Optional(Literal(':') + (SSCALE("SSCALE") | CSCALE("CSCALE")))("SCALE"))

        ### PERFS #Refaire ça, difficile à utiliser tel quel, moche, puis des trucs faux genre N signifit "entier" ici
        GlobalVoicePerf = oneOf('% $ ! !! !!! !N ? ?? ??? ?N !% ?% ?~! !~? ?~~! !~~? @~= =~@ @~~= =~~@ =') # non
        BarOrnaments = oneOf('| :| |: :|: 1 2 N $ @ >$ <$ <@ >@')# non
        NoteOrnaments = (Suppress("\\")
                         +oneOf('< > << >> + - +- -+ ++ -- =+ =- =+=- =-=+ +=* =-* DGAG DG* =~~++ =~~+ =~~-- =~~- =~~+* =~~-* =~~!! =~~! =~~?? =~~? =~~!* =~~?*')
                         +Suppress("\\")
                         )
        ChorsOrnaments = oneOf('-+ +- -~+ +~- -~~+ +~~-')

        PERFS = Suppress("\\") +(
            Optional(SSIG+Suppress(Optional("\\")))("SSIG") 
                 + Optional(BSIG+Suppress(Optional("\\")))("BSIG")
                 + ZeroOrMore(GlobalVoicePerf+Suppress(Optional("\\")))("perfs")
                 ).setWhitespaceChars("") # ordre classique clé/tempo/ "décorateurs"
        
        #ALTERATIONS
        DYNAMICALT = oneOf("! ? . _ :")
        PITCHALT = oneOf("+ - > < ~")
        ALT = DYNAMICALT | PITCHALT
        strength = (Optional(Word(nums))+ "%") | "0"
        Alteration = Group(OneOrMore(ALT) + Optional(strength))

        repetition = "*" + Optional(OneOrMore("*") | Word(nums))
        #Compact Rythm Notation

        Note = Group(
                (Optional(Alteration)("ALT")
                + Pitch
                + Optional(NoteOrnaments)
                |"@")
                 + Optional(OneOrMore("\" '")|OneOrMore(Word(nums)))
                 + Optional(repetition)
                 ).setWhitespaceChars("")

        groupedenote = Optional(Alteration) + "("+ OneOrMore(Note).setResultsName("notes",True)  + ")" + Optional(repetition)

        CRN = OneOrMore(groupedenote|Note).setResultsName("groupeandnotes",True)
        
        BEATS = Optional(";") + Word(alphas) + Optional(";")

        phrase = nestedExpr("[","]",CRN.setResultsName("CRN",True))
        group =  nestedExpr("(",")",CRN.setResultsName("CRN",True))

        #SPLIT/MERGE LINE
        BarBasedNotation = (
            Suppress(Optional("/"))+
            OneOrMore(
                Group(
                    Optional(OneOrMore(Alteration+Suppress("/")))("barAlt")
                +CRN.setResultsName("CRN",True)
                +Optional(Suppress("/")+repetition)("barRep")
                +Suppress(Optional("/"))
                )).setWhitespaceChars("")
            )

        PhraseBasedNotation = OneOrMore(
            Group(   
                    Optional(OneOrMore(Alteration))("barAlt")
                    +Suppress("[")
                    +CRN.setResultsName("CRN",True)
                    +Suppress("]")
                    +Optional(repetition)("barRep")
                    )).setWhitespaceChars(" ")
                

        splitmergecontent = BarBasedNotation.setResultsName("bars",True) #|PhraseBasedNotation.setResultsName("bars",True) # |GroupBasedNotation

        SplitLine = (Suppress(Literal("|"))
                     + splitmergecontent("content")
                     + Suppress(Optional(pythonStyleComment)))

        MergeLine = (Suppress(Literal(":"))
                     + splitmergecontent("content")
                     + Suppress(Optional(pythonStyleComment)))

        #DATALINE vars and funcs missing
        
        #defPhraseTag = varName + "=" + phrase
        #callgroupetag = 
        #phrasetag = "[" + OneOrMore(BAR) + "]"
        #groupetag =  "(" + OneOrMore(BEATS) + ")"

        #DataLine = Literal("=")("lineId") + PERFS|OneOrMore(defPhraseTag)|OneOrMore(defGroupTag)|OneOrMore(defPhraseMacro)|OneOrMore(defGroupMacro)
        DataLine = (Suppress(Literal("="))
                    + "toBeContinued"
                    + Suppress(Optional(pythonStyleComment))) #-> revoir perfs (types de perfs spécifiques attendus)
        
        LyricsLine = Literal(">")("lineId") + Word(alphas)("lyrics")
        ChordsLine = Literal("<")("lineId") + Word(alphas)("chords")

        #VOICE LINE HEADER (GLOBAL OR INSTRU)
        Instrument = Word(alphas)
        voiceLineHeader = (Suppress(Literal("O"))
                      + (Instrument("Instrument")|"global")("name")
                      + Optional(PERFS)("perfs") + Suppress(Optional(pythonStyleComment))
                      )

        #INFOLINE -> OK 
        infoKeyWord = oneOf(["title","subtitle","merge","AMN","music author","file author","lyrics author"])
        infoValue = Combine(OneOrMore(Word(alphanums+" éàè_-'ç.")))
        InfoLine = (
            (Suppress(Literal("#")) + infoKeyWord("keyWord") + Suppress("=") + infoValue("value"))
            |Suppress(Optional(pythonStyleComment))
            )

        #save file infos, suppress comments on start of line, splits blocs
        infolines = []
        i=0
        voices = []
        numBloc = -1
        for line in self.__file.splitlines():
            if line != "":
                if line[0] == "#": #info or comment if parse succeed stores infos otherwise ignores it (this was a comment)
                    inf = InfoLine.parseString(line)
                    if inf.keyWord and inf.value:
                       infolines += [inf.asDict()]
                elif line[0] == "O": #new voice bloc, creates a new entry in the voices list
                    try :
                        res = voiceLineHeader.parseString(line)
                    except:
                        e = sys.exc_info()[0]
                        print("issue at line",line,i,e)
                        raise 
                    voices += [{"line":i, "name": res.name, "perfs":res.perfs,"lines":[]}]
                    numBloc+=1
                    
                elif line[0] in "|,:,>,<,=".split(","):
                    if voices[numBloc]["name"] == "global" and line[0]!="=" :
                        raise ValueError("You must only declare dataLines (\"=\") onto global Blocs at line%i"%(i))

                    if line[0] == "|" :   # splitline
                        try :
                            res = SplitLine.parseString(line)
                        except:
                            e = sys.exc_info()[0]
                            print("issue in splitline",line,i,e)
                            raise 
                        voices[numBloc]["lines"]+=[{"type":"split","content":res.content}]
                        print("line",i)
                        for bar in res.content:
                            print("Alt",bar.barAlt, "CRN",bar.CRN,"rep", bar.barRep)
##                            for groupnote in bar.CRN:
##                                print(groupnote)
                        #print(res.asDict())
                    elif line[0] == ":" :   # mergeline
                        #assert there is a splitline to be merged with
                        if voices[numBloc]["lines"][-1]:
                            if voices[numBloc]["lines"][-1]["type"] == "split":
                                try :
                                    res = MergeLine.parseString(line)
                                except:
                                    e = sys.exc_info()[0]
                                    print("issue in mergeline",line,i,e)
                                    raise 
                                voices[numBloc]["lines"]+=[{"type":"merge","content":res.content}]
                            else :
                                raise ValueError("Merge line must be after a splitline to be merged with at line %i"%(i))
                        else :
                            raise ValueError("Merge line must be after a splitline to be merged with at line %i"%(i))

                    elif line[0] == "=" :   # dataline
                        try :
                            res = DataLine.parseString(line)
                        except:
                            e = sys.exc_info()[0]
                            print("issue in dataline",line,i,e)
                            raise 
                        voices[numBloc]["lines"]+=[{"type":"data","content":res.content}]                    
                    
                    elif line[0] == ">" :   # lyricsline
                        try :
                            res = LyricsLine.parseString(line)
                        except:
                            e = sys.exc_info()[0]
                            print("issue in lyricsline",line,i,e)
                            raise 
                        voices[numBloc]["lines"]+=[{"type":"lyrics","content":res.content}]
                        
                    elif line[0] == "<" :   # chordsline
                        try :
                            res = ChordsLine.parseString(line)
                        except:
                            e = sys.exc_info()[0]
                            print("issue in chordsline",line,i,e)
                            raise 
                        voices[numBloc]["lines"]+=[{"type":"chords","content":res.content}]                        
                else :
                    raise ValueError("Expected one of \"#, O, |, :, >, < =\", got %c at line %i"%(line[0], i))
            i+=1
        return {"infos":infolines, "voices":voices}

    @property
    def Global(self):
        return self.__Global
    
    @property
    def nbVoices(self):
        return len(self.__Voices)
    
    @property
    def title(self):
        return self.__title
    
    @title.setter
    def title(self, new):
        self.__title = new

    @property
    def AMN(self):
        return self.__AMN
    
    @AMN.setter
    def AMN(self, new):
        self.__AMN = new

    @property
    def subtitle(self):
        return self.__subtitle
    
    @subtitle.setter
    def subtitle(self, new):
        self.__subtitle = new

    @property
    def merge(self):
        return self.__merge
    
    @merge.setter
    def merge(self, new):
        self.__merge = new

    @property
    def musicauthor(self):
        return self.__musicauthor
    
    @musicauthor.setter
    def musicauthor(self, new):
        self.__musicauthor = new
    @property
    def lyricsauthor(self):
        return self.__lyricsauthor
    
    @lyricsauthor.setter
    def lyricsauthor(self, new):
        self.__lyricsauthor = new

    @property
    def fileauthor(self):
        return self.__fileauthor
    
    @fileauthor.setter
    def fileauthor(self, new):
        self.__fileauthor = new
        
    def toMIDIFile(self):
        pass
    def toLilyPondFile(self):
        pass
    def play(self):
        pass
    
class Voice(object):
    def __init__(self,file):
        self.__instrument = "kazoo" #default set to kazoo
        self.__BPM = 120 #beat per minute
        self.__BPB = 4 #beat per bar
        self.__PPB #pulses per bar ?
        pass    

print(AMNFileParser(infosong))
#print(AMNFileParser(FJ))
