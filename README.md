# AMN-python-parser

ASCII Music Notation parser to MIDI - Projet de TER 2017
---
### Structure des voix

voices: *list*:

* [ *parseResult* :
	* .name : *str*
	* .fileLine : *int*
	* .perfs : *parseResult*
		* .SSIG : *parseResult*:
			* .MPN : *str(int) or "''*
			* .IPN : *parseResult*:
				* .sign : "+" or "-" or ""
				* .pitch : *str [A-G]*
				* .octave: *str "<<" "<" ">" ">>" or [0-9]*
		* .BSIG :  *parseResult*:
			* .BPM : *str(int) or ""*
			* .dynamic : *str(int) or ""*
		* .suiteforte : *["!","!",...] or ""*
		* .factorforte : *"N" or ""*
		* .mezzoforte : *"%" or ""*
		* .suitepiano : *["?","?",...] or ""*
		* .factorpiano : *"N" or ""*
		* .mezzopiano : *"%" or ""*
		* .shortcrescendo :  *"?~!" or ""*
		* .longcrescendo :  *"?~~!" or ""*
		* .shortdecrescendo :  *"!~?" or ""*
		* .longdecrescendo :  *"!~~?" or ""*
		* .shortfadin :  *"@~=" or ""*
		* .longfadein :  *"@~~=" or ""*
		* .shortfadout :  *"=~@" or ""*
		* .longfadeout :  *"=~~@" or ""*
		* .tradexp: *str or ""*
		* .cancel: *"=" or ""* 

	* .lines : *list*
		* [*parseResult*:
			* .type : "data" or "merge" or "split" or "chord" or "lyrics"
			* .content : *list*
				* [*parseResult*:
					* .barAlt:*parseResult*
					* .barRep : *parseResult*
					* .barcontent : *list*
						* [*parseResult*:
							* .Notes : *list*
								* [*parseResult*
									* .note
									* .noteRepetition : *parseResult*
									* .noteAlteration : *parseResult*
									* .noteOrnament : *parseResult*
									* .noteTimeAlteration : *parseResult*
								* ]
						* ]
				* ]
		* ]
* ]