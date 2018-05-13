#!/usr/bin/python

##################################### IMPORT ###############################################
import sys
sys.path.append('./iptables')


import argparse
import command

##################################### PARSE ###############################################
def parseCliOptions():

    parser = argparse.ArgumentParser()

    parser.add_argument( '--command',
        dest       = 'command',
        nargs      = '+',
        type       = str,
        default    = "ls",
        help       = 'command to the get status outpot',
    )

    parser.add_argument( '--cycle',
        dest       = 'cycle',
        nargs      = '+',
        type       = int,
        default    = "5",
        help       = 'cycle time in mins',
    )


    options        = parser.parse_args()
    return options.__dict__


##################################### MAIN ###############################################

if __name__ == "__main__":
	options = parseCliOptions()
	