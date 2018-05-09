# autokraken

A set of scripts to automate the cracking of captured GSM/G2 network traffic, and to extract SMS and voice calls out of it.  This is not frequency hopping capable.

## Requirements

### Capturing

- At least two RTL dongles, as voice calls are most usually happening on another channel
- RTL drivers, the Linux kernel does the job
- RTL-SDR
- kalibrate-rtl for calibrating your device(s) in the first place
- (optional) arfcncalc to avoid using kal, grgsm_scanner or going online just to find the center frequency of a given ARFCN

## Decoding

- GNU Radio
- GR-GSM providing `grgsm_scanner`, `grgsm_capture`, `grgsm_decode`

### Cracking

- (optional) gsmframedecoder (only used when dealing with SI5)
- the unmaintained and obsolete Airprobe code base, as we did not find any equivalent for the `grm_receive.py` tool into GR-GSM
- Kraken and ready to serve rainbow tables
