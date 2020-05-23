#!/usr/bin/python3

import ujson as json

jsonfile_path = "/root/capture/CHANGE-THIS.cfile.0C.json"


# Read file
with open(jsonfile_path, 'r') as jsonfile:
	jsonobject = json.load(jsonfile)

# Parse file
tag_path = tuple(["_source","layers", "gsm_a.ccch"])
channel_description_key = "Channel Description"
keyword_internal_key = "gsm_a.dtap.msg_rr_type"
expected_value = "0x0000003f"
ignored_values = tuple(["gsm_a.rr.sdcch8_sdcchc8_cbch", "gsm_a.rr.single_channel_arfcn", "gsm_a.rr.spare"])

explain_mapping = {"tch_facch_sacchm" : "subchannel"}


for item in jsonobject:
	interesting_data = item
	for path in tag_path:
		interesting_data = interesting_data.get(path, dict())
	if interesting_data != dict() and interesting_data.get(keyword_internal_key, dict()) == expected_value:
		interesting_data = interesting_data.get(channel_description_key, dict())
		if interesting_data != dict():
			for ignore_key in ignored_values:
				if ignore_key in interesting_data.keys():
					interesting_data.pop(ignore_key)

			for key, value in interesting_data.items():
				key = key.split(".")[-1]
				if key in explain_mapping.keys():
					key = explain_mapping[key]
				print(key, ":", value)

			# print(interesting_data, "\n\n")
			print("\n")
