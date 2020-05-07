kraken=/root/KRAKEN/kraken
krakenpath=$kraken/Kraken
utilspath=$kraken/Utilities
unset kraken

usage() {
	echo 'usage: ${0##*/} <bitstring file> <plain text frame number>'
        exit 1
}

