#!/usr/bin/python

##################################### IMPORT ###############################################
import sys
sys.path.append('./iptables')

import time
import argparse
import command
import service
import apply as app

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
        default    = 20,
        help       = 'cycle time in seconds',
    )



    options        = parser.parse_args()
    return options.__dict__


##################################### MAIN ###############################################
def Run(options):
	BestList   = []
	svcl       = []

	command.DeleteAllRules()
	svcl = service.GetSvcs()
	service.PrintSvcl(svcl)
	for sv in svcl: 
   		BestList.append(app.best(sv))
   	while True: 
   		print "sleeping"
   		time.sleep(options['cycle'][0])
   		print "wakeup"
   		svcl,BestList = service.Check(svcl,BestList)
   		app.PrintBestList(BestList)






if __name__ == "__main__":
    options = parseCliOptions()
    #command.DeleteAllRules()
    Run(options)
