#!/usr/bin/python
import command

class best:
	def __init__(self, sv):
		self.svname         =    sv.name
		self.svid	        =    sv.id 
		self.svip 	        =    sv.ip 
		self.epid,self.epip =    self.ChooseBestEp(sv)
		self.ApplyBest()
	
	def ChooseBestEp(self,sv):
		#sv.UpdateSvcLatency()
		# out of range fix for i
		best = 0
		if len(sv.ep)==0:
			return "none","none"
			# add a warnning no r ep is assineg it shouldn't be called most likely the pods are not exposed to be fixed 
		minlat = sv.ep[0].lat
		for i in range(1,len(sv.ep)): 
			if sv.ep[i].lat < minlat:
				minlat=sv.ep[i].lat 
				best = i
		return sv.ep[best].id, sv.ep[best].ip

	def ApplyBest(self):
		out = command.ApplyIpRule(self.epid,self.svip)
		

