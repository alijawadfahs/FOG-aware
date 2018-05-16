#!/usr/bin/python

import commands

def OutReturn(com):
	tup = commands.getstatusoutput(com)
	return tup[1]

def GetIpRules(ID):
	print "Running " + "iptables -t nat -L "+ID
	tup = commands.getstatusoutput("iptables -t nat -L"+ID) 
	return tup[1]

