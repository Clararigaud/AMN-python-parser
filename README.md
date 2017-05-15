# AMN-python-parser
ASCII Music Notation parser to MIDI - Projet de TER 2017

voices:list
    [parseResult:
        .name : str
        .fileLine : int
        .perfs : parseResult
        .lines : list
            [parseResult:
                .type : "data" or "merge" or "split" or "chord" or "lyrics"
                    .content : list
                        [parseResult:
                            .barAlt:parseResult
                            .barRep : parseResult
                            .barcontent : list
                                [parseResult:
                                    .note : parseResult
                                    .noteRepetition : parseResult
                                    .noteAlteration : parseResult
		]
                          ]
            ]
    ]
	                
      