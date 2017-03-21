from pyparsing import *

word = Word(alphas)
INFO = OneOrMore(word)
INFOLINE = Literal("#") + INFO
VOICEID = Word(alphas)|Literal("global")
PITCH= oneOf("A B C D E F G")
OCTAVE= oneOf("<< < 0 1 2 3 4 5 6 7 8 9 > >>")
liste=''
for i in range(1,128):
    liste = liste + ' %s'%(i)
MPN = oneOf("%s"%(liste))
#MPN = Word(nums)
SIGN = oneOf("+ -")
IPN = Optional(SIGN) + PITCH + OCTAVE
EOS = IPN | MPN
SSIG = Suppress(Literal("\$")) + Optional(EOS)
VOICELINE = Literal("O") + VOICEID + SSIG + Optional(INFOLINE)
assignmentTokens = VOICELINE.parseString("O  flute \$C6 #Ceci est un commentaire")
print(assignmentTokens)
