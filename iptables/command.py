#!/usr/bin/python
import logging
LOG_FILENAME = 'command.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s',filemode='w')
import commands

def OutReturn(com): # testing purposes
	logging.info("Running " + com)
	tup = commands.getstatusoutput(com)
	return tup[1]
######################## IP RULES COMMANDS#########################################

def GetIpRules(ID):
	logging.info("Running " + "iptables -t nat -L "+ID)
	tup = commands.getstatusoutput("iptables -t nat -L "+ID) 
	while (not tup[0] == 0 ):
		logging.warning("error " + tup[1])
		tup = commands.getstatusoutput("iptables -t nat -L "+ID)
	return tup[1]

def GetIpRulesWithLineNumbers(ID):
	logging.info("Running " + "iptables --line-number -t nat -L "+ID)
	tup = commands.getstatusoutput("iptables --line-number -t nat -L "+ID)
	while (not tup[0] == 0 ):
		logging.warning("error " + tup[1])
		tup = commands.getstatusoutput("iptables --line-number -t nat -L "+ID)
	return tup[1]

def ApplyIpRule(SIP,EIP,SVNAME):
	c = CheckIpRule("OUTPUT",SIP,EIP)
	if c==0:
		logging.info("Running " + "iptables -t nat -I OUTPUT 1 ! -s 10.244.0.0/16 -d "+SIP+"/32 -j DNAT --to-destination "+EIP + " -m comment --comment " + SVNAME )
		tup=commands.getstatusoutput("iptables -t nat -I OUTPUT 1 ! -s 10.244.0.0/16 -d "+SIP+"/32 -j DNAT --to-destination "+EIP + " -m comment --comment " + SVNAME  ) 
		
	else: logging.info("trying to create an already available rule in OUTPUT chain " + str(c)+SIP)

	c  =CheckIpRule("PREROUTING",SIP,EIP)
	if  c ==0:
		logging.info("Running " + "iptables -t nat -I PREROUTING 1 ! -s 10.244.0.0/16 -d "+SIP+"/32 -j DNAT --to-destination "+EIP+ " -m comment --commen t" + SVNAME)
		tup=commands.getstatusoutput("iptables -t nat -I PREROUTING 1 ! -s 10.244.0.0/16 -d "+SIP+"/32 -j DNAT --to-destination "+EIP+ " -m comment --comment " + SVNAME)

	else: logging.info("trying to create an already available rule in PREROUTING chain " + str(c)+SIP)
	
	c = CheckIpRuleMasq(SIP)
	if c == 0:
		logging.info("Running " + "iptables -t nat -I PREROUTING 1 ! -s 10.244.0.0/16 -d "+SIP+"/32 -j KUBE-MARK-MASQ" + " -m comment --comment " + SVNAME)
		tup=commands.getstatusoutput("iptables -t nat -I PREROUTING 1 ! -s 10.244.0.0/16 -d "+SIP+"/32 -j KUBE-MARK-MASQ" + " -m comment --comment " + SVNAME)
<<<<<<< HEAD

	else: logging.info("trying to create an already available rule in PREROUTING MASQ chain " + str(c)+" "+SIP)

def CreateIpChain(name):
	logging.info("Running " + "iptables -t nat -N "+ name)
	tup = commands.getstatusoutput("iptables -t nat -N "+ name)


def ClearIpChain(name,option):
	# if option is F then the chain will be flushed if option is X the chain will be deleted
	if (option == "F") or (option == "X"):
		logging.info("Running " + "iptables -t nat -F "+ name)
		tup = commands.getstatusoutput("iptables -t nat -F"+ name)
		if option == "X":
			logging.info("Running " + "iptables -t nat -X"+ name)
			tup = commands.getstatusoutput("iptables -t nat -X"+ name)
=======

	else: logging.info("trying to create an already available rule in PREROUTING MASQ chain " + str(c)+" "+SIP)
>>>>>>> f4541ed04ba7a79574c767575ebf80190fa4978e

	print tup

def DeleteIpRuleChain(chain,ID,IP): # to be changed no nedd to be called twice
	logging.info("Deleting an IP rule " + chain + " " + ID + " " + IP )
	rules=[]
	out=GetIpRulesWithLineNumbers(chain)
	if chain == "OUTPUT":
		for x in out.splitlines():
			if ("DNAT" in x) and (IP in x):
				rules.append(int(x.replace(',','').split()[0]))

	if chain == "PREROUTING":
		for x in out.splitlines():
			if ("DNAT" in x) and (IP in x):
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

<<<<<<< HEAD
=======


def GetIpLatency(IP):
	logging.info("Running "+"ping -c 4 " + IP + " | tail -1| awk '{print $4}' | cut -d '/' -f 2")
	tup = commands.getstatusoutput("ping -c 1 " + IP + " | tail -1| awk '{print $4}' | cut -d '/' -f 2")
	if tup[1]=='':
		return 100000
	else: 
		return float(tup[1])

>>>>>>> f4541ed04ba7a79574c767575ebf80190fa4978e
def CheckIpRule(chain,SIP,EIP):
	out=GetIpRulesWithLineNumbers(chain)
	for x in out.splitlines():
		if ("DNAT" in x) and (SIP in x) and (EIP in x):
			return int(x.replace(',','').split()[0])
	return 0 

def CheckIpRuleMasq(IP):
	out=GetIpRulesWithLineNumbers("PREROUTING")
	for x in out.splitlines():
		if ("KUBE-MARK-MASQ" in x ) and (IP in x): 
			return int(x.replace(',','').split()[0])
	return 0 

def DeleteAllRules():
	DeleteIpRuleChain("OUTPUT","","")
<<<<<<< HEAD
	DeleteIpRuleChain("PREROUTING","","")


############################################ LATENCY COMMANDS ##################################

def GetIpLatency(IP):
	print "called"
	logging.info("Running "+"ping -c 4 " + IP + " | tail -1| awk '{print $4}' | cut -d '/' -f 2")
	tup = commands.getstatusoutput("ping -c 1 " + IP + " | tail -1| awk '{print $4}' | cut -d '/' -f 2")
	if tup[1]=='':
		return 100000
	else: 
		return float(tup[1])

########################################## SERF COMMANDS #########################################

def GetSerfMembers():
	logging.info("Running serf members")
	tup = commands.getstatusoutput("serf members")
	return tup[1]
	
def GetSerfRtt(node):
	logging.info("Running serf rtt " + node + " | cut -d: -f2 | cut -d ' ' -f2")
	tup = commands.getstatusoutput("serf rtt " + node + " | cut -d: -f2 | cut -d ' ' -f2")
	return float(tup[1])
=======
	DeleteIpRuleChain("PREROUTING","","")
>>>>>>> f4541ed04ba7a79574c767575ebf80190fa4978e
