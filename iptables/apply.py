#!/usr/bin/python

import command

def ApplySvc(svcl):

	for sv in svcl:
		svcID=sv.id
		svcIP=sv.ip
		#print svcIP, svcID
		for ep in sv.ep:
			ep.lat=0 


def ChooseBestEp(sv):
	sv.UpdateSvcLatency()
	best = 0
	minlat = sv.ep[0].lat
	for i in range(1,len(sv.ep)): 
		if sv.ep[i].lat < minlat:
			minlat=sv.ep[i].lat 
			best = i
	return sv.ep[best]




