import serial
from HCIEvents import HCIEvents
from BTDevice import BTDevice
import struct

import os,sys
from threading import Thread

def initserial():
	bt = serial.Serial()
	bt.port = "/dev/ttyACM0"
	bt.baudrate = 57600
	bt.open()
	return bt

def initdevice(bt):
	str = '\x01' #command
	str = str+'\x00\xFE' #GAP_DeviceInit
	str = str+struct.pack('B',struct.calcsize('BB16s16sL'))+struct.pack('BB16s16sL',8,3,'\x00','\x00',1) #ProfileRole,MaxScanRsp,IRK,CSRK,SignCounter
	
	bt.write(str)
	print "Sent device init command!"

dev = BTDevice()
bt = initserial()
dev.ser = bt
print("Connected to Dongle")
initdevice(bt)
print ""
print("Starting Read loop")


#useless key thread :)
class keythread(Thread):
	def __init__(self):
		Thread.__init__(self)
	def run(self):
		while 1:
			x=raw_input()
			if x=="d":
				BTDevice().doDiscovery()
			if x=="e":
				BTDevice().doEstablishLink(0)
			if x=="t":
				BTDevice().doTerminateLink()

thr = keythread()
thr.start()
#

while(bt.isOpen()):  #Neues DatenPAKET wird gelesen
	HCI_Packet_Type = bt.read()
	
	print("======================")
	if HCI_Packet_Type == '\x04':	#verzweigungen... hier event
		print "Found Event Packet"
		
		EVENT_CODE=bt.read()
		if EVENT_CODE=='\xFF':
			print "Vendor Specific Event Code"
		else:
			print "WHAT!?! SHOULDNT HAPPEN!!!!"
		X=bt.read(size=3)#enthaelt auch opcode
		DATA_LENGTH = struct.unpack('<BH',X)
		print "Data length :"+str(DATA_LENGTH[0])
		print "Data Code :"+str(DATA_LENGTH[1])
		HCIEvents().lookup(DATA_LENGTH[1])(DATA_LENGTH[0],bt)
	else:
		print HCI_Packet_Type
		print "broken!"
	#if BTDevice != "":
	#	bt.write(BTDevice.nextWriteCommand)
	#	BTDevice.nextWriteCommand=""