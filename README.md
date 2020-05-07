# Usage

## Stage 1

Seeking for idle frames

	cd stage1/
        cfile=/root/capture/66.hrf.cfile
        arfcn=66

Extract the timeslot (TODO: and subchannel) from Immediate Assignments


        ./json0C $cfile $arfcn
	ls -lF ${cfile}.0C.json

        ./parse.py 0C ${cfile}.0C.json

        slot=1

Look for idling frames around the Ciphering Mode Command

	./jsonXS $cfile $arfcn $slot
	ls -lF $cfile.${slot}S.json

	./parse.py XS $cfile.${slot}S.json

	plainframe=816538

## Stage 2

	cd ../stage2/

Produce the burst bit strings

	./bitstringsXS $cfile $arfcn $slot
	ls -lF $cfile.${slot}S

Tune your path to Kraken and Utilities

        vi feedcrack.lib.bash

Generate the XORs

	#./getemptyframeplain $cfile.${slot}S $plainframe
	#./getemptyframecipher $cfile.${slot}S $plainframe
	./feedemptyframe $cfile.${slot}S $plainframe

