#!/usr/bin/python3
import command
import proba
class best:
	def __init__(self, sv):
		self.svname         =    sv.name
		self.svid	        =    sv.id 
		self.svip 	        =    sv.ip 
		self.epid,self.epip =    self.ChooseBestEp(sv)
		self.sortedeps      =    self.SortEps(sv)
		#self.ApplyBest()
		self.ApplyLBBest()
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

	def ApplyLBBest(self): 
		#create a new chain for the service, it will contain all endpoints with different proba. 
		if (not command.CheckIpChain(self.svname)) or (command.CheckIpChainEmpty(self.svname)) :
			command.CreateIpChain(self.svname)
			command.ApplyIpRuleChain(self.svip,self.svname)
			k=proba.CalacK(self.sortedeps)
			for ep in self.sortedeps: 
				i=self.sortedeps.index(ep)+1
				if i!=len(self.sortedeps):
					prob= proba.CalacPi(.8,len(self.sortedeps),k,i)
					command.CreateIpRuleWithProba(self.svname,self.svip,ep.ip,prob)
				else:
					command.CreateIpRuleWithoutProba(self.svname,self.svip,ep.ip)
		else: 
			command.ApplyIpRuleChain(self.svip,self.svname)
			k=proba.CalacK(self.sortedeps)
			for ep in self.sortedeps: 
				i=self.sortedeps.index(ep)+1
				if i!=len(self.sortedeps):
					prob= proba.CalacPi(.8,len(self.sortedeps),k,i)
					if not command.CheckIpRuleWithProba(self.svname,self.svip,ep.ip,prob,i):
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
