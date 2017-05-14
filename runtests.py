from AMN_Python_Parser import *

FJ = r"""
# AMN = 1.0
# title = Frère Jacques
# ceci est un commentaire
O kazoo \$C6 # bar-based notation
|  CDEC /*/ EF G / * / G"A GF E C / * / C<G C  / *

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
>  [Hörst,du;nicht,die;Gloc;ken?]* [Ding,Dang;Dong]*"""
# le caractère antislash fait des conflits (car c'est le char qui permet
# d'echapper dans les strings python)donc il faut bien mettre un "r"
# pour "raw" avant

Imagine = r"""

#title = Imagine
#super comment
# music author = John Lennon
#lyrics author=John Lennon
#file author = Clara Sorita

O global \%72:4\ #tempo de 72 bat/ min, 4 temps par mesure
= veR1=[>%Cfa*3,Fa-Bb] veR2=[D_3|eg*3,Deg] veL3=[(<CC)*4] veL2=[(<FC)*4  ] chR1=[(>%CfF)*2,(>%CfE)*2] chR2=[( D>%CfaD , C>%CfaC] chR3=[BG>%(DbG)*2>CeG] chR4=[%Gdf   ] 
= chL=[<F <E ] chL=[<D <C ] chL=[G   ] #ver=> verse right hand / vel => verse left hand/ chr => chorus right hand etc...

O piano \$C4:C\?%\ 
| [Eg-3,Egb.%] veR2 (veR1 veR2)*4 chR1 chR2 chR3 chR4
| (veL1 veL2)*6 chL"""


infosong = r"""
# this is a comment
#title = Supersong # this is a comment
#this is a comment between two infos and it works !
# music author = Clara #this is a comment
#this is a comment
#AMN = 1.0

O global \$C4:C\%72:4\?%\?%            #wahoo
= toBeContinued #todo
= toBeContinued #todo

# there's still work to do
O barbasednotation \$C4:C\?% #perfs without closing antislash rocks
= toBeContinued
| /!/C>D*EC /*******/EF\>\ G /*59
: /CGEC/

O phrasebasednotation
| [CGEC]
"""

print(AMNFileParser(infosong))
#print(AMNFileParser(FJ))
