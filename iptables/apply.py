#!/usr/bin/python3
import command
import proba
class best:
	def __init__(self, sv, options):
		self.svname         =    sv.name
		self.svid	        =    sv.id 
		self.svip 	        =    sv.ip 
		self.epid,self.epip =    self.ChooseBestEp(sv)
		self.sortedeps      =    self.SortEps(sv)
		# TO DO: add if statements to select one of the applies. 

		#self.ApplyBest() #in case we are selecting only one best pod
		self.ApplyLBBest(options) # in case we are selecting K best pod
		#self.ApplyLBLat() # selecting the probability according to RTT of the pod
	def ChooseBestEp(self,sv):
		sv.UpdateSvcLatency()
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

	def SortEps(self,sv):
		sortedeps=[]
		for ep in sv.ep: 
			if sortedeps == []: 
				sortedeps.append(ep)
			else: 
				for sep in sortedeps: 
					if sep.lat>ep.lat:
						sortedeps.insert(sortedeps.index(sep)+1,sep)
						sortedeps[sortedeps.index(sep)]=ep
						break
					if sortedeps.index(sep) == len(sortedeps)-1:
						sortedeps.append(ep)
						break
		return sortedeps
		
	def ApplyBest(self):
		command.ApplyIpRule(self.svip,self.epip,self.svname)

	def ApplyLBBest(self,options):
		if (not command.CheckIpChain(self.svname)) or (command.CheckIpChainEmpty(self.svname)) :
			problist=proba.CalacProba(self.sortedeps,options)
			print(problist)
			command.CreateIpChain(self.svname) #create a new chain for the service, it will contain all endpoints with different proba. 
			if command.CheckIpChain(self.svname):
				command.ApplyIpRuleChain(self.svip,self.svname)
			for ep in self.sortedeps:
				i=self.sortedeps.index(ep)
				if i!=len(self.sortedeps)-1:
					command.CreateIpRuleWithProba(self.svname,self.svip,ep.ip,problist[i])
				else:
					if problist[i] != 1: 
						print("an error occurred, the last pod probability is not equal to 1")
					command.CreateIpRuleWithoutProba(self.svname,self.svip,ep.ip) #probability equal 1 since it's the last rule
		else: 
			command.ApplyIpRuleChain(self.svip,self.svname)
			for ep in self.sortedeps: 
				i=self.sortedeps.index(ep)+1
				if i!=len(self.sortedeps):
					if not command.CheckIpRuleWithProba(self.svname,self.svip,ep.ip,problist[i-1],i):
						print("entered")
						command.ClearIpChain(self.svname,"F")
						self.ApplyLBBest()
					
def UpdateBest(self):
	return

def GetIndex(sv,BestList):
	for b in BestList: 
		if sv.name == b.svname:
			return BestList.index(b)
def PrintBestList(BestList):
	for b in BestList: 
		print(b.__dict__)
