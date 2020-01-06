#!/usr/bin/python3
import logging
LOG_FILENAME = 'command.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s',filemode='w')
import subprocess as commands

def OutReturn(com): # testing purposes
	logging.info("Running " + com)
	tup = commands.getstatusoutput(com)
	return tup[1]
######################## IP RULES COMMANDS#########################################

def GetIpRules(ID):
	logging.info("Running " + "iptables -n -t nat -L "+ID)
	tup = commands.getstatusoutput("iptables -n -t nat -L "+ID)
	i=0 
	while (not tup[0] == 0 ):
		i+=1
		logging.warning("error " + tup[1])
		tup = commands.getstatusoutput("iptables -n -t nat -L "+ID)
		if i==10:
			break;
	return tup[1]

def GetIpRulesWithLineNumbers(ID):
	logging.info("Running " + "iptables -n --line-number -t nat -L "+ID +" | tail -n+3")
	tup = commands.getstatusoutput("iptables -n --line-number -t nat -L "+ID + " | tail -n+3")
	while (not tup[0] == 0 ):
		logging.warning("error " + tup[1])
		tup = commands.getstatusoutput("iptables -n --line-number -t nat -L "+ID)
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

	else: logging.info("trying to create an already available rule in PREROUTING MASQ chain " + str(c)+" "+SIP)

def ApplyIpRuleChain(SIP,SVNAME):
	c = CheckIpRule("OUTPUT",SIP,SVNAME)
	if c==0:
		logging.info("Running " + "iptables -t nat -I OUTPUT 1 ! -s 10.244.0.0/16 -d "+SIP+"/32 -j FOG-"+SVNAME)
		tup=commands.getstatusoutput("iptables -t nat -I OUTPUT 1 ! -s 10.244.0.0/16 -d "+SIP+"/32 -j FOG-"+SVNAME) 
		
	else: logging.info("trying to create an already available rule in OUTPUT chain " + str(c)+SIP)

	c  =CheckIpRule("PREROUTING",SIP,SVNAME)
	if  c ==0:
		logging.info("Running " + "iptables -t nat -I PREROUTING 1 ! -s 10.244.0.0/16 -d "+SIP+"/32 -j FOG-"+SVNAME)
		tup=commands.getstatusoutput("iptables -t nat -I PREROUTING 1 ! -s 10.244.0.0/16 -d "+SIP+"/32 -j FOG-"+SVNAME)

	else: logging.info("trying to create an already available rule in PREROUTING chain " + str(c)+SIP)
	
	c = CheckIpRuleMasq(SIP)
	if c == 0:
		logging.info("Running " + "iptables -t nat -I PREROUTING 1 ! -s 10.244.0.0/16 -d "+SIP+"/32 -j KUBE-MARK-MASQ" + " -m comment --comment " + SVNAME)
		tup=commands.getstatusoutput("iptables -t nat -I PREROUTING 1 ! -s 10.244.0.0/16 -d "+SIP+"/32 -j KUBE-MARK-MASQ" + " -m comment --comment " + SVNAME)





def CreateIpRuleWithProba(SVNAME,SIP,EIP,PROBA):
	logging.info("Running " + "iptables -t nat -m statistic --mode random -j DNAT -A FOG-"+SVNAME+" -d "+SIP+" --probability "+str(PROBA)+" --to-destination " + EIP)
	tup = commands.getstatusoutput("iptables -t nat -m statistic --mode random -j DNAT -A FOG-"+SVNAME+" -d "+SIP+" --probability "+str(PROBA)+" --to-destination " + EIP)

def CheckIpRuleWithProba(SVNAME,SIP,EIP,PROBA,i):
	logging.info("Running " + "iptables -n -t nat -L FOG-"+SVNAME+" "+str(i))
	tup = commands.getstatusoutput("iptables -n -t nat -L FOG-"+SVNAME+" "+str(i))
	if tup !=0: #rule number is not found 
		logging.info("rule number is not found")
		return False
	if PROBA !=1:
		if (SIP in tup[1]) and (EIP in tup[1]) and (str(PROBA) in tup[1]):
			return True 
	else: 
		if (SIP in tup[1]) and (EIP in tup[1]): 
			return True
	return False # rule is not found or is not in the correct position


def CreateIpRuleWithoutProba(SVNAME,SIP,EIP):
	logging.info("Running " + "iptables -t nat  -j DNAT -A FOG-"+SVNAME+" -d "+SIP+" --to-destination " + EIP)
	tup = commands.getstatusoutput("iptables -t nat  -j DNAT -A FOG-"+SVNAME+" -d "+SIP+" --to-destination " + EIP) 

def CreateIpChain(name):
	logging.info("Running " + "iptables -t nat -N FOG-"+ name)
	tup = commands.getstatusoutput("iptables -t nat -N FOG-"+ name)
def CheckIpChainEmpty(name):
	logging.info("Running " + "iptables -n -t nat -L FOG-"+ name+ " 1")
	tup = commands.getstatusoutput("iptables -n -t nat -L FOG-"+ name+" 1")
	if tup[0]==0 and tup[1]=='': 
		return True #the chain is empty
	return False #the chain have at least one rule

def CheckIpChain(name):
	logging.info("Running " + "iptables -t nat -L FOG-"+ name)
	tup = commands.getstatusoutput("iptables -n -t nat -L FOG-"+ name)
	if tup[0]== 0:
		return True #the chain is already created
	return False #the chain is not found


def ClearIpChain(name,option):
	# if option is F then the chain will be flushed if option is X the chain will be deleted
	if (option == "F") or (option == "X"):
		logging.info("Running " + "iptables -t nat -F FOG-"+ name)
		tup = commands.getstatusoutput("iptables -t nat -F FOG-"+ name)
		if option == "X":
			logging.info("Running " + "iptables -t nat -X FOG-"+ name)
			tup = commands.getstatusoutput("iptables -t nat -X FOG-"+ name)
			print("iptables -t nat -X FOG-"+ name)
			print(tup)


def DeleteIpRuleChain(chain,ID,IP): # to be changed no nedd to be called twice
	logging.info("Deleting an IP rule " + chain + " " + ID + " " + IP )
	rules=[]
	out=GetIpRulesWithLineNumbers(chain)
	if chain == "OUTPUT":
		for x in out.splitlines():
			if ("FOG-" in x) and (IP in x):
				rules.append(int(x.replace(',','').split()[0]))

	if chain == "PREROUTING":
		for x in out.splitlines():
			if ("FOG-" in x) and (IP in x):
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
	tup = commands.getstatusoutput("ping -c 1 " + IP + " | tail -1| awk '{print $4}' | cut -d '/' -f 2")
	if tup[1]=='':
		return 100000
	else: 
		return float(tup[1])

def CheckIpRule(chain,SIP,EIP):
	out=GetIpRulesWithLineNumbers(chain)
	for x in out.splitlines():
		if (SIP in x) and (EIP in x):
			return int(x.replace(',','').split()[0])
	return 0 

def CheckIpRuleMasq(IP):
	out=GetIpRulesWithLineNumbers("PREROUTING")
	for x in out.splitlines():
		if ("KUBE-MARK-MASQ" in x ) and (IP in x): 
			return int(x.replace(',','').split()[0])
	return 0 

def DeleteAllRules():
	chains=[]
	out=GetIpRulesWithLineNumbers("OUTPUT")
	for x in out.splitlines():
		if "FOG" in x:
			chains.append(x.split()[1].split("FOG-")[1])

	DeleteIpRuleChain("OUTPUT","","")
	DeleteIpRuleChain("PREROUTING","","")
	for chain in chains: 
		ClearIpChain(chain,"X")


############################################ LATENCY COMMANDS ##################################

def GetIpLatency(IP):
	print("ip: " + IP +"calculatng latency ")
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
	if not node: 
		return 1000
	logging.info("Running serf rtt " + node + " | cut -d: -f2 | cut -d ' ' -f2")
	tup = commands.getstatusoutput("serf rtt " + node + " | cut -d: -f2 | cut -d ' ' -f2")
	try:
		float(tup[1])
		return float(tup[1])
	except ValueError:
		return float(1000)

def GetHostName(): 
	logging.info("Running hostname")
	tup = commands.getstatusoutput("hostname")
	return tup[1]

