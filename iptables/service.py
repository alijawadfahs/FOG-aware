#!/usr/bin/python
import logging
import command

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
		if prob != -1 : # the probibility to redirect to this ep
			self.prob = prob
		self.lat   =   self.GetEpLatency()


	def GetEpIp(self):
		out = command.GetIpRules(self.id)
		for x in out.splitlines():
			if ((self.name and "KUBE-MARK-MASQ") in x ) and IsIpv4(x.replace(',','').split()[3]):
				return x.replace(',','').split()[3] 			

		return out 

	def GetEpLatency(self):
		return command.GetIpLatency(self.ip)

	def UpdateEpLatency(self):
		self.lat= self.GetEpLatency()
	

 
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
		#print "entered the len cond"
		return False
	for e in x : 
		if (not str.isdigit(e)):
			#print "not a digit"
			return False
		if (int(e) < 0) or (int(e) > 255):
			#print e + "for this number"
			return False
	return True 



