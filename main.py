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

		parser.add_argument( '--command',
			dest       = 'command',
			nargs      = '+',
			type       = str,
			default    = ['ls'],
			help       = 'command to the get status output',
		)

		parser.add_argument( '--cycle',
			dest       = 'cycle',
			nargs      = '+',
			type       = int,
			default    = [1],
			help       = 'cycle time in seconds',
		)

		parser.add_argument( '--alpha',
			dest       = 'alpha',
			nargs      = '+',
			type       = float,
			default    = [.8],
			help       = 'The importance of the location in scheduling',
		)

		parser.add_argument( '--LoadBalancing',
			dest       = 'LB',
			nargs      = '+',
			type       = str,
			default    = ['1-best'],
			help       = 'The function that will decide how probability should be divided over the pods',
		)
		parser.add_argument( '--K',
			dest       = 'K',
			nargs      = '+',
			type       = int,
			default    = [1],
			help       = 'number of best pods',
		)


		options        = parser.parse_args()
		return options.__dict__


##################################### MAIN ###############################################
def GetOptions(options):
	return options

def Run(options):
	BestList   = []
	svcl       = []
	command.DeleteAllRules()
	svcl = service.GetSvcs()
	service.PrintSvcl(svcl)
	for sv in svcl: 
		BestList.append(app.best(sv))
	while True: 
		print("sleeping")
		time.sleep(options['cycle'][0])
		print("wakeup")
		svcl,BestList = service.Check(svcl,BestList)
		app.PrintBestList(BestList)






if __name__ == "__main__":
		options = parseCliOptions()
		command.DeleteAllRules()
		#Run(options)


