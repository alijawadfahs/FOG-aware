#!/usr/bin/python

import commands

def OutReturn(com): # testing purposes
	print "Running " + com
	tup = commands.getstatusoutput(com)
	return tup[1]

def GetIpRules(ID):
	print "Running " + "iptables -t nat -L "+ID
	tup = commands.getstatusoutput("iptables -t nat -L "+ID) 
	return tup[1]

def GetIpLatency(IP):
	print "Running "+"ping -c 4 " + IP + " | tail -1| awk '{print $4}' | cut -d '/' -f 2"
	tup = commands.getstatusoutput("ping -c 4 " + IP + " | tail -1| awk '{print $4}' | cut -d '/' -f 2")
	if tup[1]=='':
		return 100000
	else: 
		return float(tup[1])
