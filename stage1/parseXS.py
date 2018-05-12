#! /usr/bin/env python3

import json
import math



def result():
	timeslot1 = input('choose timeslot from the list [0-8]\n')
	of = open('resultFUI.txt','w')
	for i in list_funcUI[timeslot1]:
		for j in list_cipher[timeslot1]:
			distance = int(i) - int(j)

			print ('FU=', i, 'C=', j,'\n','THe distance =' ,distance )

			if  0 <  distance < 200:
				print ('The packet Func UI ', i,  ' apperead after Cipher Packet\n') 
				of.write(i)
			elif  -200 < distance < 0:
				print ('The packet Func UI ', i, '  apperead before Cipher Packet\n') 
				of.write(i)
			else:
				print ('too much range\n')	
	of.close()

def files():
	namefile = 'mega2'
	of = open(namefile,'r')
	text = of.read()
	of.close()
	text  = json.loads(text)
	return text


def mainparse(text):
	for i in text:
		try:
			len_immediate =  i['_source']['layers']['gsm_a.ccch']['L2 Pseudo Length']['gsm_a.rr.l2_pseudo_len']
		except KeyError:
			len_immediate ='empty'

		if len_immediate =='11':
			#print ('immediate =',len_immediate)
			gsmNumber = i['_source']['layers']['gsmtap']['gsmtap.frame_nr']
			
			print (i['_source']['layers']['gsm_a.ccch'])
			print ('\n')
			#print ('GSM Number =',gsmNumber)
		else:
			pass
#print (len(text))
def testparse(text):

	#text = json.dumps(text[31]['_source']['layers'])
	#print (text)


	for i in text:
		try:
			subtimeslot =  i['_source']['layers']['gsmtap']['gsmtap.sub_slot']
			#print (i['_source']['layers']['gsm_a.dtap']['gsm_a.dtap.msg_rr_type'])
			
	##		pass
		except KeyError:
			subtimeslot = 'empty'

		if subtimeslot != 'empty':
			#print (subtimeslot)
			try:
				LengthField = i['_source']['layers']['lapdm']['lapdm.length_field']
			except KeyError:
				LengthField = 'empty'

			try:
				type_packet = i['_source']['layers']['gsm_a.dtap']['gsm_a.dtap.msg_rr_type']
			except KeyError:
				type_packet = 'empty'	

			if LengthField =='0x00000001':
				print ('SUB_slot =' ,subtimeslot)
				print ('Length Field =' ,LengthField)
				gsmNumber = i['_source']['layers']['gsmtap']['gsmtap.frame_nr']
				print ('GSM Number =',gsmNumber)
				print ('\n')
				list_funcUI[subtimeslot].append(gsmNumber)
			else:
				pass

			if type_packet == '0x00000035':
				gsmNumber = i['_source']['layers']['gsmtap']['gsmtap.frame_nr']
				print ('type packet =',type_packet)
				print ('GSM Number =',gsmNumber)
				print ('\n')
				list_cipher[subtimeslot].append(gsmNumber)
			else:
				pass
		else:
			pass


list_funcUI = {'0':[],'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[]}
list_cipher = {'0':[],'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[]}
text = files()
testparse(text)
#mainparse(text)

#pcap()
print ('Func UI ',list_funcUI,'\n')
print ('Cipher Packets ',list_cipher,'\n')

result()



