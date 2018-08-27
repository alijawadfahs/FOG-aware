#!/usr/bin/python3
import logging
import command
import apply as app
import main 
class svc: # the kubernetes services class 
	def __init__(self, svcid, svcip, svcname, svccomment):
		self.id		 = svcid # The service ID as given by Kubernetes => KUBE-SVC-XXXXXXXXXXXXXXXX where X are a character 
		self.name    = svcname #The name of the svc found in the iptables comment and using "kubectl get svc"
		self.ip 	 = svcip #The service Ip given by kubernetes extracted from the iptables
		self.comment = svccomment # The comment included in the iptables
		self.ep      = self.GetEp() # The endpoints this service redirect to

	def GetEp(self):
		out = command.GetIpRules(self.id)
		epl = []
		for x in out.splitlines():
			if (self.name  and "KUBE-SEP") in x: 
				x=x.replace(',','').split()
				if len(x) >11: 
					prob = x[12]
				else:
					prob = -1 
				x = commentfix(x)
				epl.append(ep(x[0],self.name, prob, x[5]))	
		return epl
		
	def UpdateSvcLatency(self):
		for ep in self.ep: 
			ep.UpdateEpLatency()

class ep: 
	def __init__(self, epid, name, prob, comment):
		self.id    =   epid #the Endpoint SEP given by kubernetes => KUBE-SEP-XXXXXXXXXXXXXXXX where each X is a character 
		self.name  =   name #Service name
		self.ip    =   self.GetEpIp() # The actual pod ip
		self.node  =   self.GetEpNode()
		if prob != -1 : # the probibility to redirect to this ep
			self.prob = prob
		self.lat= self.GetEpLatency()


	def GetEpIp(self):
		out = command.GetIpRules(self.id)
		for x in out.splitlines():
			if ((self.name and "KUBE-MARK-MASQ") in x ) and IsIpv4(x.replace(',','').split()[3]):
				return x.replace(',','').split()[3] 			
		return out 

	def GetEpLatency(self):
		options=main.GetOptions()
		hostname=command.GetHostName()
		if not options['serfoff']:
			if hostname==self.node:
				return options['Delay']+0.3
			else:
				return options['Delay']+command.GetSerfRtt(self.node)
		return options['Delay']+command.GetIpLatency(self.ip)

	def UpdateEpLatency(self):
		self.lat= self.GetEpLatency()

	def GetEpNode(self):
		out=command.GetSerfMembers()
		for x in out.splitlines():
			x=x.replace("ip=",'').split()
			if CheckIpForSerf(self.ip,x[3]):
				return x[0]

 
def GetSvcs():
	#the out variable should hold the output of "iptables -t nat -L KUBE-SERVICES "
	out = command.GetIpRules("KUBE-SERVICES")
	#change the output to list form
	svcl= []
	for x in out.splitlines(): # split the output to seperate lines 
		if kubesvc(x) and defaultsvc(x): # check for a user service rule
			x=commentfix(x.replace(',','').split()) #split the line into list
			svcl.append(svc(x[0],x[4],x[5].replace('/',':').split(":")[2],x[5])) # split the line into list of strings for managment purposes 
	return svcl

def Check(svcl,BestList):
	status = {}
	svcl2 = GetSvcs()
	for sv in svcl: 
		if not CheckSvc(sv):
			if GetSvIndex(sv,svcl2):
				app.PrintBestList(BestList)
				# service is changed
				DeleteSvc(sv) # to be changed the service should be added before deletion, makes a problem of deleting the new service rules. 
				del(BestList[app.GetIndex(sv,BestList)])
				BestList.append(app.best(GetSvIndex(sv,svcl2)))
				status[sv.name]="CHANGED"
			else: 
				DeleteSvc(sv)
				del(BestList[app.GetIndex(sv,BestList)])
				# service is deleted
	for sv in svcl2:
		if not GetSvIndex(sv,svcl): 
			BestList.append(app.best(GetSvIndex(sv,svcl2)))
			status[sv.name]="ADDED" 
	for b in BestList: # to be inspected more
		if b.epid =='none':
			for sv in svcl2: 

				if b.svname == sv.name:
					DeleteSvc(sv) # to be changed the service should be added before deletion, makes a problem of deleting the new service rules. 
					del(BestList[app.GetIndex(sv,BestList)])
					BestList.append(app.best(GetSvIndex(sv,svcl2),main.GetOptions()))
			#else it deletes to be implemented 

			# service is added
	#for key, value in status.iteritems():
	#print key + " : " + value
	

	return svcl2,BestList 


def CheckAllEp(sv):
	for ep in sv.ep: 
		if not CheckEp(ep,sv.id):
			return False
	return True 

def CheckAllSv(sv,svcl):
	for svi in svcl:
		if sv.name==svi.name and sv.ip==svi.ip and sv.id==svi.id:
			return True
	return False


def CheckEp(ep,svid):
	out = command.GetIpRules(svid)
	if ep.id in out: 
		out = command.GetIpRules(ep.id)
		if ep.ip in out: 
			return True
	return False



def CheckSvc(sv):
	svcl = GetSvcs()
	svi = GetSvIndex(sv,svcl)
	if svi: # the service is available
		for ep in sv.ep: 
			if not CheckEp(ep,sv.id):
				return False
				#logiing info an EP is changed
	else:
		return False
		#logiing info a sevice is deleted
	return True


def GetSvIndex(sv,svcl):
	for svi in svcl:
		if sv.name==svi.name and sv.ip==svi.ip and sv.id==svi.id:
			return svi
	return 

def DeleteAllSvc(svcl):
	for sv in svcl: 
		DeleteSvc(sv)


def DeleteSvc(sv):
	command.DeleteIpRuleChain("OUTPUT",sv.id,sv.ip)
	command.DeleteIpRuleChain("PREROUTING",sv.id,sv.ip)

def PrintSvcl(svcl):
	names=[]
	for sv in svcl: 
		names.append(sv.name)
	print(names)


################################### condition checking ############################
def kubesvc(out):
	return "KUBE-SVC" in out

def defaultsvc(out):
	return ("default" in out) and (not "default/kubernetes:https" in out) 
	
def commentfix(out):
	i=0
	y=[]
	for x in out: 
		if i<6: 
			y.append(x)
			i+=1
		else:
			y[5]+=' '+x 
	return y


def IsIpv4(ip):
	x = ip.split('.')
	if len(x) != 4:
		return False
	for e in x : 
		if (not str.isdigit(e)):
			return False
		if (int(e) < 0) or (int(e) > 255):
			return False
	return True 
def CheckIpForSerf(epip,serfip):
	epip=epip.split('.')
	serfip=serfip.split('.')
	for x in range(3):
		if epip[x]!=serfip[x]:
			return False
	return True



