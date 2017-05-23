\header {
title="Gammes" 
meter = "30"
}
choeurs=\relative c{\clef bass c4  d4  e4  f4  g4  a4  b4  c } 
ocarina=\relative c''{ c4  d4  e4  f4  g4  a4  b4  c } 
<<\new Staff { \time4/4\choeurs}
\new Staff { \time4/4\ocarina}
>>