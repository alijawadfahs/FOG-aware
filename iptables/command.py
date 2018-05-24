#!/usr/bin/python
import logging
LOG_FILENAME = 'command.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
import commands

def OutReturn(com): # testing purposes
	logging.info("Running " + com)
	tup = commands.getstatusoutput(com)
	return tup[1]

def GetIpRules(ID):
	logging.info("Running " + "iptables -t nat -L "+ID)
	tup = commands.getstatusoutput("iptables -t nat -L "+ID) 
	return tup[1]
def applyIpRule(ID,IP):
	return

def GetIpLatency(IP):
	logging.info("Running "+"ping -c 4 " + IP + " | tail -1| awk '{print $4}' | cut -d '/' -f 2")
	tup = commands.getstatusoutput("ping -c 4 " + IP + " | tail -1| awk '{print $4}' | cut -d '/' -f 2")
	if tup[1]=='':
		return 100000
	else: 
		return float(tup[1])
