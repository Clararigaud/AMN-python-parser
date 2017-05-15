from pyparsing import *

GlobalVoicePerf = oneOf('% $ ! !! !!! !N ? ?? ??? ?N !% ?% ?~! !~? ?~~! !~~? @~= =~@ @~~= =~~@ =') # non
BarOrnaments = oneOf('| :| |: :|: 1 2 N $ @ >$ <$ <@ >@')# non
NoteOrnaments = (Suppress("\\")
                 +oneOf('< > << >> + - +- -+ ++ -- =+ =- =+=- =-=+ +=* =-* DGAG DG* =~~++ =~~+ =~~-- =~~- =~~+* =~~-* =~~!! =~~! =~~?? =~~? =~~!* =~~?*')
                 +Suppress("\\")
                 )
Pitch = Word(srange('[A-G]'),exact=1,max=1)
#ALTERATIONS
DYNAMICALT = oneOf("! ? . _ :")
PITCHALT = oneOf("+ - > < ~")
ALT = DYNAMICALT | PITCHALT
strength = (Optional(Word(nums))+ "%") | "0"
Alteration = Group(OneOrMore(ALT) + Optional(strength))

repetition = "*" + Optional(OneOrMore("*") | Word(nums))
#Compact Rythm Notation
ToneRepetition = Literal("\"") | Literal("'") |OneOrMore(Word(nums))
Note = Group((Optional(Alteration)("ALT")
        + (Pitch |Literal("@"))("note").setWhitespaceChars("")
        + Optional(NoteOrnaments)("ornament")
        ).setWhitespaceChars("")
         + Optional(Group(OneOrMore(ToneRepetition)))("noterepetition")
         + Optional(repetition)
         ).setWhitespaceChars("")

Notes = Group(OneOrMore(Note).setWhitespaceChars("")).setResultsName("Notes")
NotesGroup = Group(Optional(Alteration)
                +  nestedExpr("(",")",Notes)
                + Optional(repetition)).setWhitespaceChars("")("GroupNotes")

CRN = OneOrMore(Word(printables, excludeChars="\n [ ] / "))
s = "A' %B''''' +CD"

res = CRN.parseString(s)
print(res)

