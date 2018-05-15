#!/usr/bin/python
import commands

class svc: 
	def __init__(self, svcid, svcip, svcname, svccomment):
		self.id		 = svcid # The service ID as given by Kubernetes => KUBE-SVC-XXXXXXXXXXXXXXXX where X are a character 
		self.name    = svcname #The name of the svc found in the iptables comment and using "kubectl get svc"
		self.ip 	 = svcip #The service Ip given by kubernetes extracted from the iptables
		#self.pods	 = podip #the adresses of the pod ip addresses
		self.comment = svccomment # The comment included in the iptables
	def getep(self):



def getsvcs(out):
	#the out variable should hold the output of "iptables -t nat -L KUBE-SERVICES -v "
	return getsvc(out, 1)




def getsvc(out, ln):
	#the out variable should hold the output of "iptables -t nat -L KUBE-SERVICES ln --line-number -v " where ln is the line number
	if(out==""):
		#add a log info that the output is not passed
		print "ERROR: the output is not passed"
		return []
	else:
		outlines=[x.split(";")[0].replace(',',' ').split() for x in out.splitlines() if x]
		return outlines[ln]

