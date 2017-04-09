from pyparsing import *

### Perfs
GlobalVoicePerf = oneOf('% $ ! !! !!! !N ? ?? ??? ?N !% ?% ?~! !~? ?~~! !~~? @~= =~@ @~~= =~~@ =')
BarOrnaments = oneOf('| :| |: :|: 1 2 N $ @ >$ <$ <@ >@')
NoteOrnaments = oneOf('< > << >> + - +- -+ ++ -- =+ =- =+=- =-=+ +=* =-* DGAG DG* =~~++ =~~+ =~~-- =~~- =~~+* =~~-* =~~!! =~~! =~~?? =~~? =~~!* =~~?*')
ChorsOrnaments = oneOf('-+ +- -~+ +~- -~~+ +~~-')
perfs = GlobalVoicePerf | BarOrnaments | NoteOrnaments | ChorsOrnaments

### Scale Signature
Octave = oneOf('<< < 0 1 2 3 4 5 6 7 8 9 > >>')
Pitch = oneOf('A B C D E F G')
Sign = oneOf('+ -')
Key = Optional(Sign) + oneOf('A B C D E F G a b c d e f g')
Fifth = '0' | Sign + oneOf('1 2 3 4 5 6 7')
Degree = Word(alphas)
Sscale = Key | Fifth
Lower = OneOrMore("-") + Optional(Optional(Word(nums) | "%"))
Raise = OneOrMore("+") + Optional(Optional(Word(nums) | "%"))
Freq = "="+ Word(nums) + Optional(oneOf("' Hz"))
Tone = Word(alphas)
MPN = Word(nums) #entre 0 et 127
IPN = Optional(Sign) + Pitch + Octave
EOS = MPN | IPN
Step = Tone + (Freq | Raise) + Lower + Raise + Degree
Cscale = Literal('[') + Step + Literal('$]')

Ssig = Literal('\$') + EOS + Optional(Literal(':') + (Sscale | Cscale))

### Beat Signature

Int = Word(nums)
Pattern = Optional(oneOf(":  ")) + Int 
SBeat = Word(nums)
CBeat = Literal('[')+ (Pattern | (Literal('/')+Pattern) | (Literal(' ')+Pattern) ) + Literal(']')
BPB = Word(nums) #default 120
BPM = Word(nums)#default 4
Bsig = Literal('\%') + BPM + Optional(Literal('~') + BPM) + Optional(Literal(':') + (SBeat | CBeat))

### Compact Chord Notation

CCN = OneOrMore(oneOf('. - + H M m Q X x S s N n L T t A B C D E F G'))

### Alterations
altchars = oneOf('! ? . _ : + - < > ~')
ALT = OneOrMore(altchars) +  Optional((Word(nums) | oneOf("0 %")))

#BAR = OneOf((SSIG) + (BSIG)
BAR = Optional("/")+OneOrMore(Key)+Optional("/")
BEATS = Optional(";") + Word(alphas) + Optional(";")



Info = OneOrMore(Word(alphas))
InfoLine = Literal('#') + Group(Info)
voicename = Word(alphas)
VoiceIdentifier = ("global"|voicename)
SplitLine = "|" + OneOrMore(BAR)
MergeLine = ":" + OneOrMore(BAR)
phrasetag = "[" + OneOrMore(BAR) + "]"
groupetag =  "(" + OneOrMore(BEATS) + ")"
#DataLine = "=" + perfs|phrasetag|groupetag|callphrasetag|callgroupetag
DataLine = "=" + perfs
VoiceParamLine = DataLine|SplitLine|MergeLine
VoiceLine = "O" + VoiceIdentifier + Optional(Ssig) + Optional(Bsig) +Optional(perfs)

VoiceBloc = VoiceLine + Optional(OneOrMore(VoiceParamLine))
File = Optional(OneOrMore(InfoLine)) + OneOrMore(VoiceBloc)
aze = "O flute \$C6:C #Voici un exemple"

ddd= File.parseString(aze)
print(ddd)

