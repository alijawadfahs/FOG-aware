#!/usr/bin/python
import logging
LOG_FILENAME = 'command.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s',filemode='w')
import commands

def OutReturn(com): # testing purposes
	logging.info("Running " + com)
	tup = commands.getstatusoutput(com)
	return tup[1]

def GetIpRules(ID):
	logging.info("Running " + "iptables -t nat -L "+ID)
	tup = commands.getstatusoutput("iptables -t nat -L "+ID) 
	return tup[1]

def GetIpRulesWithLineNumbers(ID):
	logging.info("Running " + "iptables --line-number -t nat -L "+ID)
	tup = commands.getstatusoutput("iptables --line-number -t nat -L "+ID) 
	return tup[1]

def ApplyIpRule(ID,IP):
	c = CheckIpRule("OUTPUT",ID,IP)
	if c==0:
		logging.info("Running " + "iptables -t nat -I OUTPUT 1 ! -s 10.244.0.0/16 -d "+IP+"/32 -j "+ID)
		tup=commands.getstatusoutput("iptables -t nat -I OUTPUT 1 ! -s 10.244.0.0/16 -d "+IP+"/32 -j "+ID) 

	else:  logging.info("trying to create an already available rule in OUTPUT chain " + str(c)+ID)

	c  = CheckIpRule("PREROUTING",ID,IP)
	if  c ==0:
		logging.info("Running " + "iptables -t nat -I PREROUTING 1 ! -s 10.244.0.0/16 -d "+IP+"/32 -j "+ID)
		tup=commands.getstatusoutput("iptables -t nat -I PREROUTING 1 ! -s 10.244.0.0/16 -d "+IP+"/32 -j "+ID)

	else:  logging.info("trying to create an already available rule in PREROUTING chain " + str(c)+ID)
	c = CheckIpRuleMasq(IP)
	if c == 0:
		logging.info("Running " + "iptables -t nat -I PREROUTING 1 ! -s 10.244.0.0/16 -d "+IP+"/32 -j KUBE-MARK-MASQ")
		tup=commands.getstatusoutput("iptables -t nat -I PREROUTING 1 ! -s 10.244.0.0/16 -d "+IP+"/32 -j KUBE-MARK-MASQ")

	else:  logging.info("trying to create an already available rule in PREROUTING MASQ chain " + str(c)+" "+ID)


def DeleteIpRuleChain(chain,ID,IP): # to be changed no nedd to be called twice
	logging.info("Deleting an IP rule " + chain + " " + ID + " " + IP )
	rules=[]
	out=GetIpRulesWithLineNumbers(chain)
	if chain == "OUTPUT":
		for x in out.splitlines():
			if ("KUBE-SEP-" in x) and (IP in x):
				rules.append(int(x.replace(',','').split()[0]))

	if chain == "PREROUTING":
		for x in out.splitlines():
			if ("KUBE-SEP-" in x) and (IP in x):
				rules.append(int(x.replace(',','').split()[0]))
			if ("KUBE-MARK-MASQ" in x ) and (IP in x):
				rules.append(int(x.replace(',','').split()[0]))
	rules = sorted(rules)
	if rules: 
		out2 =GetIpRulesWithLineNumbers(chain)
		if out==out2:
			i=0
			for rule in rules:
				rule-=i
				DeleteIpRule(chain,rule)
				i+=1
			if CheckIpRule(chain,ID,IP) == 0 or CheckIpRuleMasq(IP) == 0:# add the mask condition
				return True
			else:
				DeleteIpRuleChain(chain,ID,IP)

		else: 
			DeleteIpRuleChain(chain,ID,IP)
			# add a warrning log 
			 
def DeleteIpRule(chain,rule):
	logging.info("iptables -t nat -D "+chain +" " + str(rule))
	tup = commands.getstatusoutput("iptables -t nat -D "+chain +" " + str(rule))
	return tup[1]



def GetIpLatency(IP):
	logging.info("Running "+"ping -c 4 " + IP + " | tail -1| awk '{print $4}' | cut -d '/' -f 2")
	tup = commands.getstatusoutput("ping -c 4 " + IP + " | tail -1| awk '{print $4}' | cut -d '/' -f 2")
	if tup[1]=='':
		return 100000
	else: 
		return float(tup[1])

def CheckIpRule(chain,ID,IP):
	out=GetIpRulesWithLineNumbers(chain)
	for x in out.splitlines():
		if ("KUBE-SEP-" in x) and ((ID and IP) in x):
			return int(x.replace(',','').split()[0])
	return 0 

def CheckIpRuleMasq(IP):
	out=GetIpRulesWithLineNumbers("PREROUTING")
	for x in out.splitlines():
		if ("KUBE-MARK-MASQ" in x ) and (IP in x): 
			return int(x.replace(',','').split()[0])
	return 0 