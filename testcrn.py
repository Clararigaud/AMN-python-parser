from pyparsing import *

GlobalVoicePerf = oneOf('% $ ! !! !!! !N ? ?? ??? ?N !% ?% ?~! !~? ?~~! !~~? @~= =~@ @~~= =~~@ =') # non
BarOrnaments = oneOf('| :| |: :|: 1 2 N $ @ >$ <$ <@ >@')# non
NoteOrnaments = (Suppress("\\")
                 +oneOf('< > << >> + - +- -+ ++ -- =+ =- =+=- =-=+ +=* =-* DGAG DG* =~~++ =~~+ =~~-- =~~- =~~+* =~~-* =~~!! =~~! =~~?? =~~? =~~!* =~~?*')
                 +Suppress("\\")
                 )
Pitch = Word(srange('[A-G]'),exact=1)
#ALTERATIONS
DYNAMICALT = oneOf("! ? . _ :")
PITCHALT = oneOf("+ - > < ~")
ALT = DYNAMICALT | PITCHALT
strength = (Optional(Word(nums))+ "%") | "0"
Alteration = Group(OneOrMore(ALT) + Optional(strength))

repetition = "*" + Optional(OneOrMore("*") | Word(nums))
#Compact Rythm Notation
ToneRepetition = Literal("\"") | Literal("'") |OneOrMore(Word(nums))
Note = ((Optional(Alteration)("ALT")
        + (Pitch |Literal("@"))
        + Optional(NoteOrnaments)
        )
         + Group(Optional(OneOrMore(ToneRepetition)))
         + Optional(repetition)
         )

NotesGroup = (Optional(Alteration)
                +  nestedExpr("(",")",OneOrMore(Note))
                + Optional(repetition)).setWhitespaceChars("")

Notes = OneOrMore(Note).setResultsName("note",True).setWhitespaceChars("")

TimeEl = Group(OneOrMore(Note,stopOn=" ")).setResultsName("el",True)
CRN = OneOrMore(TimeEl).setWhitespaceChars(" ")

s = "A AA"

res = CRN.parseString(s)
print(res.asDict())
