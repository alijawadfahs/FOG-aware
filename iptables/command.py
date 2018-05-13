#!/usr/bin/python

import commands

def Out_Return(str):
	tup = commands.getstatusoutput(str)
	return tup[1]
