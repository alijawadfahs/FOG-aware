#!/usr/bin/python3

##################################### IMPORT ###############################################
import sys
sys.path.append('./iptables')

import time
import argparse
import command
import service
import apply as app
import proba
##################################### PARSE ###############################################
def parseCliOptions():

		parser = argparse.ArgumentParser()

		parser.add_argument( '--command', #imp
			dest       = 'command', 
			type       = str,
			default    = 'ls',
			help       = 'command to the get status output',
		)

		parser.add_argument( '--cycle',#imp
			dest       = 'cycle',  
			type       = int,
			default    = 1,
			help       = 'cycle time in seconds',
		)

		parser.add_argument( '--alpha', #imp 
			dest       = 'alpha',
			type       = float,
			default    = .8,
			help       = 'The importance of the location in scheduling',
		)

		parser.add_argument( '--LoadBalancing', #imp
			dest       = 'LB',
			type       = str,
			default    = '1-best',
			help       = 'The function that will decide how probability should be divided over the pods',
		)
		parser.add_argument( '--K', #imp
			dest       = 'K',
			type       = int,
			default    = -1,
			help       = 'number of best pods',
		)
		parser.add_argument( '--serfoff', #imp
			dest       = 'serfoff',
			action     = 'store_true',
			help       = 'use serf for latency calculation or use ping',
		)
		
		options        = parser.parse_args()
		return options.__dict__


##################################### MAIN ###############################################
def GetOptions():
	options = parseCliOptions()
	return options

def Run(options):
	BestList   = []
	svcl       = []
	command.DeleteAllRules()
	svcl = service.GetSvcs()
	service.PrintSvcl(svcl)
	for sv in svcl: 
		BestList.append(app.best(sv,options))
	while True: 
		print("sleeping")
		time.sleep(options['cycle'])
		print("wakeup")
		svcl,BestList = service.Check(svcl,BestList)
		app.PrintBestList(BestList)






if __name__ == "__main__":
		options = parseCliOptions()
		#command.DeleteAllRules()
		Run(options)


