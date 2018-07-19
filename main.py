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
<<<<<<< HEAD
        default    = [5],
=======
        default    = 20,
>>>>>>> f4541ed04ba7a79574c767575ebf80190fa4978e
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
<<<<<<< HEAD
	for sv in svcl:
		for ep in sv.ep: 
			print ep.__dict__ 
=======
	for sv in svcl: 
>>>>>>> f4541ed04ba7a79574c767575ebf80190fa4978e
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
<<<<<<< HEAD
    #Run(options)


=======
    Run(options)
>>>>>>> f4541ed04ba7a79574c767575ebf80190fa4978e
