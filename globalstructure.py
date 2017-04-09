from pyparsing import *
FJ = """
# AMN = 1.0
# title = Frère Jacques
# ceci est un commentaire
O kazoo \$C6 # bar-based notation
|  CDEC / * / EF G / * / G"A GF E C / * / C<G C  / *

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
>  [Hörst,du;nicht,die;Gloc;ken?]* [Ding,Dang;Dong]*""".splitlines()

Imagine = """
#title=Imagine
#music author=John Lennon
#lyrics author=John Lennon

O global /74%:4/ #tempo de 72 bat/ min, 4 temps par mesure
= veR1=[>%Cfa*3,Fa-Bb] veR2=[D_3|eg*3,Deg] veL3=[(<CC)*4] veL2=[(<FC)*4  ] chR1=[(>%CfF)*2,(>%CfE)*2] chR2=[( D>%CfaD , C>%CfaC] chR3=[BG>%(DbG)*2>CeG] chR4=[%Gdf   ] 
= chL=[<F <E ] chL=[<D <C ] chL=[G   ] #ver=> verse right hand / vel => verse left hand/ chr => chorus right hand etc...

O piano \$C4:C\ ?%\ 
| [Eg-3,Egb.%] veR2 (veR1 veR2)*4 chR1 chR2 chR3 chR4
| (veL1 veL2)*6 chL""".splitlines()

class AMNFileParser(object):
    def __init__(self,AMNFile):

        self.__file = AMNFile #make checkups
        # params à remplir avec les infos issues des infolines
        self.__version = None
        self.__title = None
        self.__subtitle = None
        self.__merge = None
        self.__musicauthor = None
        self.__lyricsauthor = None
        self.__fileauthor = None
        
        self.parseFile()
        print("Success !")
        print("AMN version:", self.version)
        print("Title:", self.title)
        print("subtitle:", self.subtitle)
        print("Music Author:", self.musicauthor)
        print("Lyrics Author:", self.lyricsauthor)
        print("File Author:", self.fileauthor)
        print("File to merge:", self.merge)
        print("Nb Voices:",self.nbVoices)

    def parseFile(self):
        content = Word(alphanums+"\$* /[]:!><;,?._=%()-" )
        
        #VOICE LINE
        voicename = Word(alphas)
        VoiceIdentifier = ("global"|voicename)
        VoiceLine = Literal("O")("lineId") + VoiceIdentifier + Optional(content) 

        infoKeyWord = oneOf("title subtitle merge") | Literal("AMN").setParseAction(replaceWith("version")) | Literal("music author").setParseAction(replaceWith("musicauthor")) | Literal("lyrics author").setParseAction(replaceWith("lyricsauthor")) | Literal("file author").setParseAction(replaceWith("fileauthor"))
        infoValue = Combine(OneOrMore(Word(alphanums+" éàè_-'ç.")))
        InfoLine = Literal("#")("lineId") + infoKeyWord("keyWord") + "=" + infoValue("value")
        SplitLine = Literal("|")("lineId") + content 
        MergeLine = Literal(":")("lineId") + content 
        LyricsLine = Literal(">")("lineId") + content
        ChordsLine = Literal("<")("lineId") + content
        #DataLine = "=" + perfs|phrasetag|groupetag|callphrasetag|callgroupetag
        DataLine = Literal("=")("lineId") + content
        Line = (VoiceLine | InfoLine |SplitLine|MergeLine|LyricsLine|ChordsLine|DataLine|Suppress(pythonStyleComment)) + Suppress(Optional(pythonStyleComment))

        vB = -1
        self.__Voices = []
        
        for line in self.__file:
            if line != "":
                res = Line.parseString(line)
                if res.lineId == "O":
                    vB+=1
                    self.__Voices += [0]
                    self.__Voices[vB]=[]
                    
                if res.lineId == "#": # InfoLine
                    setattr(self,res.keyWord,res.value) #Makes it an attribute 
                    
                elif res.lineId in "|,:,>,<,=".split(",") : #Option line for current Voice
                    self.__Voices[vB] += [res]

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
    def version(self):
        return self.__version
    
    @version.setter
    def version(self, new):
        self.__version = new

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
        #self.instrument
        pass    

AMNFileParser(Imagine)
AMNFileParser(FJ)
