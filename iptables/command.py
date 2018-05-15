#!/usr/bin/python

import commands

def Out_Return(com):
	tup = commands.getstatusoutput(com)
	return tup[1]
