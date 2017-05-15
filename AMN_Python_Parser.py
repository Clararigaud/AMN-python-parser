from pyparsing import *
import sys

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
        parsed = self.parseFile()
        
        for info in parsed["infos"]:
            #Makes it an attribute
            setattr(self,info["keyWord"].replace(" ", ""),info["value"])
        self.__Voices = parsed["voices"]
        self.__Global = parsed["global"]

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
        CBEAT = (Suppress(Literal('['))
                 + (PATTERN | (Literal('/')+PATTERN) | (Literal(' ')+PATTERN))
                 + Suppress(Literal(']'))
                 )
        BSIG= (Suppress(Literal('%'))
               + Optional(BPM| dynamicBPM)
               + Optional(Literal(':')
                          + (SBEAT | CBEAT))
               )

        #SSIG a l'air OK
        Octave = oneOf('<< < > >>')|Word(srange("[0-9]"),exact=1)
        Pitch = Word(srange('[A-G]'),exact=1)
        Sign = oneOf('+ -')
        Key = Optional(Sign) + (Word(srange("[A-G]"),exact=1)("MAJOR")
                                | Word(srange("[a-g]"),exact=1)("MINOR"))
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
        SSIG = Group(Suppress(Literal('$'))
                + EOS("EOS")
                + Optional(Literal(':')
                           + (SSCALE("SSCALE") | CSCALE("CSCALE")))("SCALE")
                )

        GlobalVoicePerf = oneOf('% $ ! !! !!! !N ? ?? ??? ?N !% ?% ?~! !~? ?~~! !~~? @~= =~@ @~~= =~~@ =') # non
        BarOrnaments = oneOf('| :| |: :|: 1 2 N $ @ >$ <$ <@ >@')# non

#=========================================================
        NoteOrnaments = (Suppress("\\")
                         +oneOf('< > << >> + - +- -+ ++ -- =+ =- =+=- =-=+ +=* =-* DGAG DG* =~~++ =~~+ =~~-- =~~- =~~+* =~~-* =~~!! =~~! =~~?? =~~? =~~!* =~~?*')
                         +Suppress("\\")
                         )
        ChordsOrnaments = oneOf('-+ +- -~+ +~- -~~+ +~~-')

        #ECN = Chords Notations CCN and ECN to be done
        PERFS = Suppress("\\") +(
            Optional(SSIG.setResultsName("SSIG") +Suppress(Optional("\\")))
                 + Optional(BSIG+Suppress(Optional("\\")))("BSIG")
                 + ZeroOrMore(GlobalVoicePerf+Suppress(Optional("\\")))("voiceperfs")
                 ).setWhitespaceChars("") # ordre classique clé/tempo/ "décorateurs"
        
        #ALTERATIONS
        DYNAMICALT = oneOf("! ? . _ :")
        PITCHALT = oneOf("+ - > < ~")
        ALT = DYNAMICALT("dynamic") | PITCHALT("pitch")
        strength = (Optional(Word(nums))+ "%") | "0"
        Alteration = Group(OneOrMore(ALT) + Optional(strength))

        repetition = "*" + Optional(OneOrMore("*") | Word(nums))
        #Compact Rythm Notation
        ToneRepetition = Literal("\"") | Literal("'") |OneOrMore(Word(nums))
        
        Note = ((Optional(Alteration)("noteAlteration")
                + (Pitch |Literal("@"))("note")
                + Optional(NoteOrnaments)("noteOrnament")
                )
                 + Group(Optional(OneOrMore(ToneRepetition)))("timeAlteration")
                 + Optional(repetition)("noteRepetition")
                 ).setWhitespaceChars("")
        Notes = OneOrMore(Note.setResultsName("Notes",True))
        NotesGroup = Group(Optional(Alteration)
                        +  nestedExpr("(",")",Notes)
                        + Optional(repetition)).setWhitespaceChars("")

        TimeEl = Notes|NotesGroup
#==============================================
        CRN = OneOrMore(Word(printables, excludeChars="\n [ ] / "))
        
        BEATS = Optional(";") + Word(alphas) + Optional(";")

        group =  nestedExpr("(",")",CRN)

        #SPLIT/MERGE LINE
        BarBasedNotation = Group(
            Suppress(Optional("/"))+
            OneOrMore(
                Group(
                    Optional(OneOrMore(Alteration+Suppress("/")))("barAlt")
                +Group(Group(CRN)).setResultsName("barcontent")
                +Optional(Suppress("/")+repetition)("barRep")
                +Suppress(Optional("/"))
                ).setWhitespaceChars(""))
            ).setResultsName("bars")

        PhraseBasedNotation = Group(
                OneOrMore(Group(
                    Optional(OneOrMore(Alteration))("barAlt")
                    +nestedExpr("[","]",CRN).setResultsName("barcontent")
                    +Optional(repetition)("barRep")
                    ))).setResultsName("bars")
                
        splitmergecontent = BarBasedNotation |PhraseBasedNotation # |GroupBasedNotation

        SplitLine = (Suppress(Literal("|"))
                     + splitmergecontent.setResultsName("content")
                     + Suppress(Optional(pythonStyleComment)))

        MergeLine = (Suppress(Literal(":"))
                     + splitmergecontent.setResultsName("content")
                     + Suppress(Optional(pythonStyleComment)))
        
        #DATALINE vars and funcs missing
        
        #defPhraseTag = varName + "=" + phrase
        #callgroupetag = 
        #phrasetag = "[" + OneOrMore(BAR) + "]"
        #groupetag =  "(" + OneOrMore(BEATS) + ")"

        #DataLine = Literal("=")("lineId") + PERFS|OneOrMore(defPhraseTag)|OneOrMore(defGroupTag)|OneOrMore(defPhraseMacro)|OneOrMore(defGroupMacro)
        DataLine = (Suppress(Literal("="))
                    + PERFS("perfs")
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
            (Suppress(Literal("#"))
             + infoKeyWord("keyWord")
             + Suppress("=")
             + infoValue("value"))
            |Suppress(Optional(pythonStyleComment))
            )

        #save file infos, suppress comments on start of line, splits blocs
        infolines = []
        i=0
        voices = []
        globalVoiceId = None
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
                        print("issue at line",i,line,e)
                        raise
                    res.fileLine = i
                    res.lines =[]
                    voices += [res]
                    
                    numBloc+=1
                    if res.name == "global":
                        if globalVoiceId != None :
                            raise ValueError("There must only be one global bloc line%i"%(i))
                        globalVoiceId = numBloc
                    
                elif line[0] in "|,:,>,<,=".split(","):
                    if voices[numBloc].name == "global" and line[0]!="=" :
                        raise ValueError("You must only declare dataLines (\"=\") onto global Blocs at line%i"%(i))

                    if line[0] == "|" :   # splitline
                        try :
                            res = SplitLine.parseString(line)
                        except:
                            e = sys.exc_info()[0]
                            print("issue in splitline",i,line,e)
                            raise
                        res.type="split"
                        res.fileLine = i
                        voices[numBloc].lines+=[res]

                        #parsing bars
                        for i in range(len(res.content)):    
                            res.content[i].barcontent = [TimeEl.parseString(timel) for timel in res.content[i].barcontent[0]]      
                                    
                    elif line[0] == ":" :   # mergeline
                        try :
                            res = MergeLine.parseString(line)
                        except:
                            e = sys.exc_info()[0]
                            print("issue in mergeline",i,line,e)
                            raise
                        res.fileLine = i
                        res.type="merge"
                        voices[numBloc].lines+=[res]
                        #parsing bars
                        for i in range(len(res.content)):    
                            res.content[i].barcontent = [TimeEl.parseString(timel) for timel in res.content[i].barcontent[0]]
                            
                    elif line[0] == "=" :   # dataline
                        try :
                            res = DataLine.parseString(line)
                        except:
                            e = sys.exc_info()[0]
                            print("issue in dataline",i,line,e)
                            raise
                        res.type ="data"
                        res.fileLine = i
                        voices[numBloc].lines+=[res]                    
                        
                    elif line[0] == ">" :   # lyricsline
                        try :
                            res = LyricsLine.parseString(line)
                        except:
                            e = sys.exc_info()[0]
                            print("issue in lyricsline",i,line,e)
                            raise
                        res.type = "lyrics"
                        res.fileLine = i
                        voices[numBloc].lines+=[res]
                        
                    elif line[0] == "<" :   # chordsline
                        try :
                            res = ChordsLine.parseString(line)
                        except:
                            e = sys.exc_info()[0]
                            print("issue in chordsline",i,line,e)
                            raise
                        res.type = "chords"
                        res.fileLine = i
                        voices[numBloc].lines+=[res]                        
                else :
                    raise ValueError("Expected one of \"#, O, |, :, >, < =\", got %c at line %i"%(line[0], i))
            i+=1
        GlobalBloc = None
        if globalVoiceId != None:
            GlobalBloc = voices.pop(globalVoiceId)
        return {"infos":infolines, "voices":voices, "global" : GlobalBloc }

    @property
    def Global(self):
        return self.__Global

    @property
    def Voices(self):
        return self.__Voices 
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
| /!/C>D*EC /*******/EF\>\ G /*59
: /C GEC/

O phrasebasednotation \$C4:C\%72:4\?%\?%   
| [CGEC] [C GEC]

O barbasednotation
| /CGEC/
"""
verre = r"""
#title=Remplis ton verre vide
#music author=Etienne Daniel
#Chanson à deux voix d'après une chanson à boire de XVIIe s

O global \$ F : D \% 208 : 4\

O chant  \$ F : D
| [@""A A]** [D""DC'B][A""A'A][G'FE'A][AA B][F""F]

O flute
| /!/C>D*EC /*******/EF\>\ G /*59
: /CGEC/CG EC/CGE C/
"""
boogie = r"""
#------------------------------------------------------------------------------------------------------------------------------------
#title= Boogie
#Et est-ce que c'est comme en musique quand il y a des dièses et des bémol? Cad que le dièses s'applique sur toute la mesure? 
O piano \$C5\%120:4\
| [+DE GG +DE GG] [+DE CC @'] [+GA >C>C +GA >C>C] [GF EC @'] [B+D BG A>C AF] [+DE CC @']
= \$C4\
: [CG CG CG CG] [CG CG -BG >C] [>%FC >%FC >%FC >%FC] [CG CG -BG >C] [>%GD >%GD >%FD >%FD] [CG CG -BG >C] #chord notation
#est-ce qu'on peut mettre le égal comme ça, suivit d'un merge?
"""
if __name__ == "__main__":
    parsed = AMNFileParser(infosong)
    print(parsed)

    print(parsed.Voices[0].name)
    print(parsed.Voices[0].lines[0].type)
    for bar in parsed.Voices[0].lines[0].content:
        print("Bar repetition :",bar.barRep)
        print("Bar alteration :",bar.barAlt)
        for timel in bar.barcontent:
            for note in timel.Notes:
                print("note",note.note,"alteration",note.noteAlteration,"ornament",note.noteOrnament,"repetition",note.noteRepetition,"timealteration",note.timeAlteration)
