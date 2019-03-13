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
				return options['Delay']+options['local']
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

def Check(svcl,BestList,options):

	#checking for added svc's:
	svcl2 = GetSvcs() #checking the services 
	for sv in svcl2:
		if not GetSvIndex(sv,svcl):
			print("SERVICE "+ sv.name+ " IS ADDED")
			BestList.append(app.best(sv,options))
	

	#checking for deleted svc's:
	delsv=[]
	for sv in svcl:
		if GetSvIndex(sv,svcl2)==False:
			print("SERVICE "+ sv.name + " IS DELETED")
			DeleteSvc(sv,"X")# delete the iptables rules
			delsv.append(sv) # to be deleted from the list 
			del(BestList[app.GetIndex(sv,BestList)])# delete from the apply list
	for sv in delsv: 
		del(svcl[svcl.index(sv)])

	#checking for edited svc's:
	for sv1 in svcl: 
	# 	for e in sv1.ep:
	# 		if not CheckEp(e,sv1.id): # a pod have failed
		for sv2 in svcl2:	
		 	if (sv1.name==sv2.name) and (sv1.ip==sv2.ip) and (sv1.id==sv2.id):
		 		for e1 in sv1.ep:
		 			temp=0
		 			for e2 in sv2.ep:
		 				if (e1.ip==e2.ip) and (e1.id==e2.id):
		 					temp=1
		 					break 
		 			if temp==0: # the pod is removed
		 				print(e1.ip+ "  FAILED")
		 				BestList=UpdateSvc(sv2,BestList,options)
		 				break

		 		for e1 in sv2.ep:
		 			temp=0
		 			for e2 in sv1.ep:
		 				if (e1.ip==e2.ip) and (e1.id==e2.id):
		 					temp=1
		 					break 
			 			if temp==0: # the pod is added
			 				print(e2.ip+ " is INJECTED")
			 				BestList=UpdateSvc(sv2,BestList,options)
			 				break
		 		break
			
	return svcl2,BestList

def UpdateSvc(sv,BestList,options):
	DeleteSvc(sv,"F")# delete the iptables rules
	del(BestList[app.GetIndex(sv,BestList)])
	BestList.append(app.best(sv,options))
	return BestList

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



def CheckSvc(sv,svcl):
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
		if (sv.name==svi.name) and (sv.ip==svi.ip) and (sv.id==svi.id):
			return True
	return False

def DeleteAllSvc(svcl):
	for sv in svcl: 
		DeleteSvc(sv)


def DeleteSvc(sv,option):
	command.DeleteIpRuleChain("OUTPUT",sv.name,sv.ip)
	command.DeleteIpRuleChain("PREROUTING",sv.name,sv.ip)
	command.ClearIpChain(sv.name,option)

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



