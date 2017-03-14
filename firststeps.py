#ASCII MUSIC NOTATION - PARSER

from pyparsing import *

""" Grammaire

-----------------------------------
convenient notation for what comes:
(optionnal)
1Or+ one or more allowed
"" literal (literally what's between the "'s)
-----------------------------------
Top down for the readability

    File -> 1Or+InfoLine + 1Or+VoiceBloc
    InfoLine -> "#" + info 
    VoiceBloc -> VoiceLine + (1Or+VoiceParamLine)
    VoiceLine -> "O" + VoiceIdentifier + (SSIG) + (BSIG) +(perfs)
    VoiceParamLine -> DataLine|SplitLine|MergeLine
    DataLine -> "=" + perfs|phrasetag|groupetag|callphrasetag|callgroupetag
    MergeLine -> ":" + 1Or+bar
    SplitLine -> "|" + 1Or+bar
    VoiceIdentifier -> "global"|anychars
    bar -> (SSIG) + (BSIG) 
    SSIG -> anychars   (4now)
    BSIG -> anychars   (4now)
    perfs -> anychars   (4now)

"""

file = """
#  ...
#  AMN=1.0
#  title= Frère Jacques
#  subtitle=Le tube de l'année

O  global ...
=  \...\...\...\
=  a=[...] b=[...]
=  a=(...) b=(...)
=  f(x,y)=[...]
=  g(x,y)=(...)
=  c=[...f(C,5)...]
=  d=(...f(C,5)...)

O  vox \...\...\
O  guitar \...\...\

O  vox \...\...\
|  .../.../.../...
:  .../.../.../...
=  \...\...\...\
|  .../.../.../...
:  .../.../.../...
O  guitar \...\...\
=  a=[...] b=[...]
|  a* b*
|  c=[...] [c]
"""
