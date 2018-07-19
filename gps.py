#!/usr/bin/python

from math import sin, cos, sqrt, atan2, radians
import serial 
import argparse
fname="sample.out"


class point: 
	def __init__(self,lat,lon,node): 
		self.lat      =     lat
		self.lon      =     lon 
		self.node     =     node 

	def CalcDistance(self,p): 
		R = 6373.0
		lat1 = radians(self.lat)
		lon1 = radians(self.lon)
		lat2 = radians(p.lat)
		lon2 = radians(p.lon)

		dlon = lon2 - lon1
		dlat = lat2 - lat1

		a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
		c = 2 * atan2(sqrt(a), sqrt(1 - a))

		return  R * c

def parseCliOptions():

    parser = argparse.ArgumentParser()

    parser.add_argument( '--command',
        dest       = 'command',
        nargs      = '+',
        type       = str,
        default    = ['ls'],
        help       = 'command to the get status output',
    )
    options        = parser.parse_args()
    return options.__dict__

def GetGPRMC():
	gps= serial.Serial('/dev/ttyS0', 9600)
	line= gps.readline()
	while True :
		CheckGPRMC(line)
		line= gps.readline()

def ReturnCoordinates(line):
	data = line.split(',')
	if ('GPRMC' in data[0]) and (data[2] == 'A'):
		lat = float(data[3])
		lat = int(lat/100) + (lat - int(lat/100)*100)/60 
		lon = float(data[5]) 
		lon = int(lon/100) + (lon - int(lon/100)*100)/60 
		if data[4] == "S": 
			lat = lat *- 1 
		if data[6] == "W": 
			lon = lon * -1  
		return (lat,lon)
	return False 
		





###################################### MAIN  ##################################

if __name__ == "__main__":
	options = parseCliOptions() # to be removed
	GetGPRMC()
	with open(fname) as f:
		for line in f: 
			print ReturnCoordinates(line)

	p1=point(48.116951, -1.639997,'node1')
	p2=point(48.116991, -1.639810,'node2')
	print p1.CalcDistance(p2)*1000

