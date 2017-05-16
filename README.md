# AMN-python-parser

ASCII Music Notation parser to MIDI - Projet de TER 2017
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
					* .barAlt: *parseResult*
					* .barRep : *parseResult*
						* .repsuite : *["\*,\*,.."] or ""*
						* .repfactor : *str(int) or ""*
					* .barcontent : *list*
						* [*parseResult*:
							* .Notes : *list*
								* [*parseResult*
									* .note : *str [A-G]*
									* .noteRepetition : *parseResult*
										* .repsuite : *["\*,\*,.."]*
										* .repfactor : *str(int) or ""*
									* .noteAlteration : *parseResult*
										* .dynamic : * parseResult *
											* .alt : "char"  
											* .strenght : [] 
										* pitch : * parseResult *
											* .alt : "char"  
											* .strenght : [] 
									* .noteTimeAlteration : *parseResult*
									* .noteOrnament : *parseResult*
										* .leftshortsyncopa : *"<" or ""*
										* .rightshortsyncopa : *">" or ""*
										* .leftlongsyncopa : *"<<" or ""*
										* .rightlongsyncopa : *">>" or ""*
										* .upperacciaccatura : *"+" or ""*
										* .loweracciaccatura : *"-" or ""*
										* .upperdoubleacciaccatura : *"+-" or ""*
										* .lowerdoubleacciaccatura : *"-+" or ""*
										* .upperappogiatura : *"++" or ""*
										* .lowerappogiatura : *"--" or ""*
										* .uppermordent : *"=+" or ""*
										* .lowermordent : *"=-" or ""*
										* .uppergruppetto : *"=+=-" or ""*
										* .lowergruppetto : *"=+\*" or ""*
										* .uppertrill : *"=-\*" or ""*
										* .lowertrill : *"=-=+" or ""*
										* .strongupperpitchbend : *"=~~++" or ""*
										* .weakupperpitchbend : *"=~~+" or ""*
										* .stronglowerpitchbend : *"=~~--" or ""*
										* .weaklowerpitchbend : *"=~~+\*" or ""*
										* .strongtremolo : *"=~~-\*" or ""*
										* .weaktremolo : *"=~~-" or ""*
										* .strongmodulationincrease : *"=~~!!" or ""*
										* .weakmodulationincrease : *"=~~!" or ""*
										* .strongmodulationdecrease : *"=~~??" or ""*
										* .weakmodulationdecrease : *"=~~!\*" or ""*
										* .strongvibrato : *"=~~?\*" or ""*
										* .weakvibrato : *"=~~?" or ""*
										* .explicitgracenote *"[A-G]"*
										* .explicittremolo *"[A-G]"*
								* ]
						* ]
				* ]
		* ]
* ]