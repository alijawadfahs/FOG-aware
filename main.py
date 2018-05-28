#!/usr/bin/python

##################################### IMPORT ###############################################
import sys
sys.path.append('./iptables')


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
        default    = 5,
        help       = 'cycle time in mins',
    )



    options        = parser.parse_args()
    return options.__dict__


##################################### MAIN ###############################################

if __name__ == "__main__":
    options = parseCliOptions()
    svcl = service.GetSvcs()
    BestList=[]
    service.PrintSvcl(svcl)
    command.DeleteAllRules()
    for sv in svcl: 
    	BestList.append(app.best(sv))
    
    
    #service.Check(svcl,BestList)
    #service.DeleteAllSvc(svcl)
    while (True):
    	raw_input("Press Enter to continue...")
    	service.PrintSvcl(svcl)
    	service.Check(svcl,BestList)
    #command.DeleteAllRules()
