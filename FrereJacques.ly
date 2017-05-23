\header {
arranger="Christophe Schlick" 
title="Frere Jacques" 
meter = "60"
}
sifflet=\relative c'{\repeat percent2{ c4  d4  e4  c4 } \repeat percent2{ e4  f4  g2 } \repeat percent2{ g8.  a16  g8  f8  e4  c4 } \repeat percent2{ c4  g  c2 } } 
siffletaaaa=\relative c'{\repeat percent2{ e4  f4  g4  e4 } \repeat percent2{ g4  a4  b2 } \repeat percent2{ b8.  c16  b8  a8  g4  e4 } \repeat percent2{ e4  b  e2 } } 
violoncelle=\relative c{\clef bass\repeat percent2{ e4  f4  g4  e4 } \repeat percent2{ g4  a4  b2 } \repeat percent2{ b8.  c16  b8  a8  g4  e4 } \repeat percent2{ e4  b  e2 } } 
sifflet=\relative c'{\repeat percent2{ c4  d4  e4  c4 } \repeat percent2{ e4  f4  g2 } \repeat percent2{ g8.  a16  g8  f8  e4  c4 } \repeat percent2{ c4  g  c2 } } 
siffletaaaa=\relative c'{\repeat percent2{ e4  f4  g4  e4 } \repeat percent2{ g4  a4  b2 } \repeat percent2{ b8.  c16  b8  a8  g4  e4 } \repeat percent2{ e4  b  e2 } } 
<<\new GrandStaff<<\set GrandStaff.instrumentName = #"sifflet" \new Staff { \time4/4\sifflet}
 \new Staff { \siffletaaaa}
>>
\new Staff { \time4/4\violoncelle}
\new GrandStaff<<\set GrandStaff.instrumentName = #"sifflet" \new Staff { \time4/4\sifflet}
 \new Staff { \siffletaaaa}
>>
>>