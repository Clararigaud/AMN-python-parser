from pyparsing import *
import sys

class AMNFileParser(object):
    def __init__(self,AMNFile):
        with open(AMNFile, 'r') as enter:
            self.__file = enter.read()
        #self.__file = AMNFile #make checkups
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

    #PERFS==================================================================================
        #BEAT SIGNATURE=====================================================================       
        INT = Word(nums)
        PATTERN = Optional(oneOf(":  ")) + INT 
        SBEAT = Word(nums)
        CBEAT = (Suppress(Literal('['))
                 + (PATTERN | (Literal('/')+PATTERN) | (Literal(' ')+PATTERN))
                 + Suppress(Literal(']'))
                 )
        
        BPM = Word(nums)
        BSIG= (Suppress(Literal('%'))
               + Optional(BPM("BPM") + Optional( Suppress("~") + BPM("dynamic")))
               + Optional(Literal(':')
                          + (SBEAT | CBEAT))("BEAT")
               )
        #SCALE SIGNATURE====================================================================
        Sign = oneOf('+ -')
        
        Key = Optional(Sign)("sign") + Word(srange("[A-G]")+srange("[a-g]"),exact=1)("note")
        Fifth = '0' | Sign + Word(srange("[1-7]"),exact=1)
        Degree = Word(alphas)
        SSCALE = Key("scalekey") | Fifth("fifth")
        Lower = OneOrMore("-") + Optional(Optional(Word(nums) | "%"))
        Raise = OneOrMore("+") + Optional(Optional(Word(nums) | "%"))
        Freq = "="+ Word(nums) + Optional(oneOf("' Hz"))
        Tone = Word(alphas)
        Step = Tone + (Freq | Raise) + Lower + Raise + Degree
        CSCALE = Literal('[') + Step + Literal('$]')

        Pitch = Word(srange('[A-G]'),exact=1)
        Octave = oneOf('<< < > >>')|Word(srange("[0-9]"),exact=1)        
        MPN = Word(nums) #entre 0 et 127 
        IPN = (Optional(Sign)("sign")
               + Pitch("pitch")
               + Optional(Octave)("octave")
               ).setWhitespaceChars("")
        EOS = MPN("MPN") | IPN("IPN")
        SSIG = Group(Suppress(Literal('$'))
                + EOS
                + Optional(Suppress(Literal(':'))
                           + (SSCALE("SSCALE") | CSCALE("CSCALE")))
                )
        
        #GLOBALVOICEPERFS===================================================================        
        GlobalVoicePerf = (
                (
                    Group(Literal("!")+OneOrMore(Literal("!")))("suiteforte")
                    |(Suppress(Literal("!"))+Word(nums)("factorforte"))
                    |(Suppress(Literal("!"))+Literal("%")("mezzoforte"))
                    )
                |(
                    Group(Literal("?")+OneOrMore(Literal("?")))("suitepiano")
                    |(Suppress(Literal("?"))+Word(nums)("factorpiano"))
                    |(Suppress(Literal("?"))+Literal("%")("mezzopiano"))
                    )
            |(
                (
                    Literal("?~!")("shortcrescendo")
                    |Literal("?~~!")("longcrescendo")
                    )
                |(
                    Literal("!~?")("shortdecrescendo")
                    |Literal("!~~?")("longdecrescendo")
                    )
                )
            |(
                (
                    Literal("@~=")("shortfadein")
                    |Literal("@~~=")("longfadein")
                    )
                |(
                    Literal("=~@")("shortfadeout")
                    |Literal("=~~@")("longfadeout")
                    )
            
                )
            |Combine(Word(alphas+" "))("tradexp") #traditionnal expression
            |Literal("=")("cancel")
            )

        PERFS = ( # ordre classique clé/tempo/ "décorateurs"
            Suppress("\\")
            +(
                Optional(SSIG.setResultsName("SSIG")+Suppress(Optional("\\")))
                 + Optional(BSIG+Suppress(Optional("\\")))("BSIG")
                 + ZeroOrMore(
                     GlobalVoicePerf
                     +Suppress(Optional("\\"))
                     ).setResultsName("volumealteration",True)
                 ).setWhitespaceChars("")) 

  #ALTERATIONS =============================================================================
        strength = Optional(Word(nums))+ Optional(Literal("%"))
        DYNAMICALT = (Group(OneOrMore(Literal("!")))
                      |Group(OneOrMore(Literal("?")))
                      |Group(OneOrMore(Literal(".")))
                      |Group(OneOrMore(Literal("_")))
                      |Group(OneOrMore(Literal(":")))
                      
                      )("alt")+ Optional(strength("strength"))
        PITCHALT = (Group(OneOrMore(Literal("+")))
                      |Group(OneOrMore(Literal("-")))
                      |Group(OneOrMore(Literal(">")))
                      |Group(OneOrMore(Literal("<")))
                      |Group(OneOrMore(Literal("~")))
                      )("alt")+ Optional(strength("strength"))

        Alteration = (
            (DYNAMICALT("dynamic"))
             |(PITCHALT("pitch")) 
            )
  #REPETITIONS =============================================================================
        repetition = (
            (Suppress(Literal("*"))+Word(nums)("repfactor"))
            | Group(OneOrMore("*"))("repsuite")
            )
  #CHORDS ======================= NOT OK ===================================================
        #Chords Notations CCN and ECN to be done
        ChordsOrnaments = oneOf('-+ +- -~+ +~- -~~+ +~~-')
        
  #NOTES ===================================================================================
        NoteOrnament = ( #mystery capte certains elements et d'autres non. Je comprend pas. 
                         Literal("<")("leftshortsyncopa")
                         |Literal(">")("rightshortsyncopa")
                         |Literal("<<")("leftlongsyncopa")
                         |Literal(">>")("rightlongsyncopa")
                         |Literal("+")("upperacciaccatura")
                         |Literal("-")("loweracciaccatura")
                         |Literal("+-")("upperdoubleacciaccatura")
                         |Literal("-+")("lowerdoubleacciaccatura")
                         |Literal("++")("upperappogiatura")
                         |Literal("--")("lowerappogiatura")
                         |Literal("=+")("uppermordent")
                         |Literal("=-")("lowermordent")
                         |Literal("=+=-")("uppergruppetto")
                         |Literal("=-=+")("lowergruppetto")
                         |Literal("=+*")("uppertrill")
                         |Literal("=-*")("lowertrill")
                         |Literal("=~~++")("strongupperpitchbend")
                         |Literal("=~~+")("weakupperpitchbend")
                         |Literal("=~~--")("stronglowerpitchbend")
                         |Literal("=~~-")("weaklowerpitchbend")
                         |Literal("=~~+*")("strongtremolo")
                         |Literal("=~~-*")("weaktremolo")
                         |Literal("=~~!!")("strongmodulationincrease")
                         |Literal("=~~!")("weakmodulationincrease")
                         |Literal("=~~??")("strongmodulationdecrease")
                         |Literal("=~~?")("weakmodulationdecrease")
                         |Literal("=~~!*")("strongvibrato")
                         |Literal("=~~?*")("weakvibrato")
                         |OneOrMore(Pitch)("explicitgracenote")
                         |(OneOrMore(Pitch)("explicittremolo")
                           +Suppress(Literal("*")))
                         )
        
        timealteration = Literal("\"") | Literal("'") |OneOrMore(Word(nums))

        Note = (Optional(OneOrMore(Alteration))("noteAlteration")
                + (Pitch |Literal("@"))("note")
                + Optional(Suppress(Literal("\\"))+NoteOrnament("noteOrnament")+Suppress(Literal("\\")))
                +(Optional(OneOrMore(timealteration))("timeAlteration"))
                + Optional(repetition("noteRepetition"))
                ).setWhitespaceChars("")
        Notes = OneOrMore(Note.setResultsName("Notes",True))
        NotesGroup = Group(Optional(Alteration)
                        +  nestedExpr("(",")",Notes)
                        + Optional(repetition)).setWhitespaceChars("")

        TimeEl = Notes|NotesGroup

        #parsing en deux temps
        CRN = OneOrMore(Word(printables, excludeChars="\n [ ] / "))
        BEATS = Optional(";") + Word(alphas) + Optional(";")

# BARS =====================================================================================
    #ORNAMENTS ==================== NOT DONE ===============================================
        group =  nestedExpr("(",")",CRN)
        BarOrnaments = oneOf('| :| |: :|: 1 2 N $ @ >$ <$ <@ >@')# non
    #BAR BASED NOTATION ====================================================================
        BarBasedNotation = Group(
            Suppress(Optional("/"))+
            OneOrMore(
                Group(
                    Optional(OneOrMore(Alteration+Suppress("/")))("barAlt")
                +Group(Group(CRN)).setResultsName("barcontent")
                    #ornament
                +Optional(Suppress("/")+repetition("barRep"))
                +Suppress(Optional("/"))
                ).setWhitespaceChars(""))
            ).setResultsName("bars")   
    #PHRASE BASED NOTATION =================================================================
        PhraseBasedNotation = Group(
                OneOrMore(Group(
                    Optional(OneOrMore(Alteration))("barAlt")
                    +nestedExpr("[","]",CRN).setResultsName("barcontent")
                    #ornament
                    +Optional(repetition("barRep"))
                    ))).setResultsName("bars")
    #LINES =================================================================================                
        #SPLIT & MERGE =====================================================================
        splitmergecontent = BarBasedNotation |PhraseBasedNotation # |GroupBasedNotation
        SplitLine = (Suppress(Literal("|"))
                     + splitmergecontent.setResultsName("content")
                     + Suppress(Optional(pythonStyleComment)))
        MergeLine = (Suppress(Literal(":"))
                     + splitmergecontent.setResultsName("content")
                     + Suppress(Optional(pythonStyleComment)))
        #DATALINE ==========================================================================
        #defPhraseTag = varName + "=" + phrase
        #callgroupetag = 
        #phrasetag = "[" + OneOrMore(BAR) + "]"
        #groupetag =  "(" + OneOrMore(BEATS) + ")"
        #DataLine = Literal("=")("lineId") + PERFS|OneOrMore(defPhraseTag)|OneOrMore(defGroupTag)|OneOrMore(defPhraseMacro)|OneOrMore(defGroupMacro)
        DataLine = (Suppress(Literal("="))
                    + PERFS("perfs")
                    + Suppress(Optional(pythonStyleComment)))
        # LYRICS & CHORDS ==================================================================
        LyricsLine = Literal(">")("lineId") + Word(alphas)("lyrics")
        ChordsLine = Literal("<")("lineId") + Word(alphas)("chords")
        #BLOC HEADER (GLOBAL OR INSTRU)=====================================================
        Instrument = Word(alphas)
        voiceLineHeader = (Suppress(Literal("O"))
                      + (Instrument("Instrument")|"global")("name")
                      + (
                          Optional(PERFS)("perfs")
                          + Suppress(Optional(pythonStyleComment)))
                      )
        #INFOLINE ==========================================================================
        infoKeyWord = oneOf(
            ["title",
             "subtitle",
             "merge",
             "AMN",
             "music author",
             "file author",
             "lyrics author"
             ])
        infoValue = Combine(OneOrMore(Word(alphanums+" éàè_-'ç.")))
        InfoLine = (
            (Suppress(Literal("#"))
             + infoKeyWord("keyWord")
             + Suppress("=")
             + infoValue("value"))
            |Suppress(Optional(pythonStyleComment))
            )
    #MAIN PARSE LOOP========================================================================
        #parsing lines one by one
        #separate comments from infolines, stores infolines and voice blocs
        infolines = []
        i=0
        voices = []
        globalVoiceId = None
        numBloc = -1
        for line in self.__file.splitlines():
            if line != "":
                if line[0] == "#":
                    #info or comment if parse succeed stores infos
                    #otherwise ignores it (this was a comment)
                    inf = InfoLine.parseString(line)
                    if inf.keyWord and inf.value:
                       infolines += [inf.asDict()]
                elif line[0] == "O":
                    #new voice bloc, creates a new entry in the voices list
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
                            raise ValueError(
                                "There must only be one global bloc line%i"%(i)
                                )
                        globalVoiceId = numBloc
                    
                elif line[0] in "|,:,>,<,=".split(","):
                    if voices[numBloc].name == "global" and line[0]!="=" :
                        raise ValueError(
                            "You must only declare dataLines into global at line%i"%(i)
                            )

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
                            res.content[i].barcontent = [
                                TimeEl.parseString(timel)
                                for timel in res.content[i].barcontent[0]
                                ]      
                                    
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
                            res.content[i].barcontent = [
                                TimeEl.parseString(timel)
                                for timel in res.content[i].barcontent[0]
                                ]
                            
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
                    raise ValueError(
                        "Expected one of \"#,O,|,:,>,<,=\", got %c at line %i"%(line[0], i))
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

if __name__ == "__main__":
    parsed = AMNFileParser("demos/frerejacques.amn")
    print(parsed)
                        
