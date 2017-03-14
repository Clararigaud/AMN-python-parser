from pyparsing import *
""" BNF grammaire
P ::= SN + SV
SV ::= (AUX) + VERBE + SN
SN ::= ART + NOM
AUX ::= va
VERBE ::= lire|lit|mange
ART ::= le|la|les|un|une|des
NOM ::= garçon|livre|pomme
"""

NOM = Word(alphas)
ART = oneOf("le la les un une des")
VERBE = Word(alphas)
SN = Group(ART.setResultsName("article") + NOM.setResultsName("nom"))
AUX = Literal("va")
ADJ = Word(alphas).setResultsName("adjectif")
SV =  Optional(AUX).setResultsName("auxiliaire") + VERBE.setResultsName("verbe") + (SN.setResultsName("gnominal")|ADJ)
P = SN.setResultsName("groupenominal") + SV.setResultsName("gverbal")
phrases = ["le garcon mange une pomme", "le garcon va lire un livre", "le ciel est bleu"]

for phrase in phrases :
    print("\nphrase :", phrase)   
    res = P.parseString(phrase)
    print("groupe nominal :", res.groupenominal,"\n groupe verbal : ", res.gverbal)
    print(res)




