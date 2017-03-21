from pyparsing import *

### Perfs

GlobalVoicePerf = oneOf('% $ ! !! !!! !N ? ?? ??? ?N !% ?% ?~! !~? ?~~! !~~? @~= =~@ @~~= =~~@ =')
BarOrnaments = oneOf('| :| |: :|: 1 2 N $ @ >$ <$ <@ >@')
NoteOrnaments = oneOf('< > << >> + - +- -+ ++ -- =+ =- =+=- =-=+ +=* =-* DGAG DG* =~~++ =~~+ =~~-- =~~- =~~+* =~~-* =~~!! =~~! =~~?? =~~? =~~!* =~~?*')
ChorsOrnaments = oneOf('-+ +- -~+ +~- -~~+ +~~-')

Info = OneOrMore(Word(alphas))
InfoLines = Group(Literal('#') + Info)
VoiceIdentifier = Word(alphas)
Voice = Word(alphas)

### Scale Signature

Octave = oneOf('<< < 0 1 2 3 4 5 6 7 8 9 > >>')
Pitch = oneOf('A B C D E F G')
Sign = oneOf('+ -')
Key = Optional(Sign) + oneOf('A B C D E F G a b c d e f g')
Fifth = '0' | Sign + oneOf('1 2 3 4 5 6 7')
Sscale = Key | Fifth
Lower = oneOf('-N -- --% - -%')
Raise = oneOf('+N ++ ++% + +%')
Freq = oneOf('=N =N =NHz')
Tone = Word(alphas)
MPN = Word(nums)
IPN = Group(Pitch + Octave)
EOS = MPN | IPN
Step = Group(Tone + (Freq | Raise) + Lower + Raise)
Cscale = Literal('[') + Step + Literal('$]')
Ssig = Literal('\$') + EOS + Optional(Group(Literal(':') + (Sscale | Cscale)))
Degree = Word(alphas)

### Beat Signature

Int = Word(nums)
Pattern = Int | Literal('/')+Int | Literal(' ')+Int
SBeat = Word(nums)
CBeat = Literal('[')+ (Pattern | (Literal('/')+Pattern) | (Literal(' ')+Pattern) ) + Literal(']')
BPB = Word(nums)
BPM = Word(nums)
Bsig = Literal('\%') + BPM + Optional(Group(Literal('~') + BPM)) + Optional(Literal(':') + (SBeat | CBeat))

### Compact Chord Notation

CCN = oneOf('. - + H M m Q X x S s N n L T t A B C D E F G')

### Alterations

ALT = oneOf('! ? . _ : + - < > ~')

File = Literal('O')  + Voice + Ssig + InfoLines

aze = "O flute \$C6:C #Voici un exemple"

ddd= File.parseString(aze)
print(ddd)

