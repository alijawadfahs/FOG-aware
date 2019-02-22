import main
import math

def gettheoptions(): 
	options=main.GetOptions()
	print(options)

############################################## Best pods ######################################
#This file will contain the probability equations used with the iptables.
#The probability of the rule #i is equal to pi, however these probabilities dosen't reflect the probability of accessing the pods.
#Pi is the probability of acheiving the rule, which means that the probability of accessing the pod is equal to the probability of the current rules multiplied by the probabilities of not taking the previous rules. 
#a is alpha variable, selected by the user using the arguments, and it reflects the importance in proximity. 
#n is the number of the pod in the replicaset. 
#k is the number of prefered pods over the others according to latency. 
#i is the index of the rule/pod.
#PK is the probability of the first rule. 

def CalacProba(SEP,options): 
	prob    = []
	podprob = []
	lat     = []
	sumall  = 0 
	a       = options['alpha']
	b       = options['Beta']
	if options['LB'] == '1-best':
		k = CalacK(SEP,options)
		print("k= " + str(k))
		for ep in SEP: 
			i = SEP.index(ep)
			if (i+1)!=len(SEP):
				prob.append(CalacPi(a,len(SEP),k,i+1))
			else :
				prob.append(1)
	if options['LB'] == 'e(-x)':
		for ep in SEP:
			lat.append(ep.lat)
		for l in lat: 
			sumall+= math.exp(-b*l)
		for l in lat: 
			podprob.append(math.exp(-b*l)/sumall)
		for p in podprob:
			podprob[podprob.index(p)]=a*p+(1-a)*(1/len(SEP))
		print("pod probability: "+ str(podprob))
		return CalacProbFromPod(podprob)

	if options['LB'] == '1/x':
		for ep in SEP:
			lat.append(ep.lat)
		for l in lat: 
			sumall+= 1/math.pow(l,b)
		for l in lat: 
			podprob.append((1/(math.pow(l,b)))/sumall)
		for p in podprob:
			podprob[podprob.index(p)]=a*p+(1-a)*(1/len(SEP))
		print("pod probability: "+ str(podprob))
		return CalacProbFromPod(podprob)

	if options['LB'] == '1/x2':
		for ep in SEP:
			lat.append(ep.lat)
		for l in lat: 
			sumall+= 1/(b*l)
		for l in lat: 
			podprob.append((1/(b*l))/sumall)
		for p in podprob:
			podprob[podprob.index(p)]=a*p+(1-a)*(1/len(SEP))
		print("pod probability: "+ str(podprob))
		return CalacProbFromPod(podprob)

	return prob


def CalacPK(a,n,k,i):
	if i>k  and i <= 0 :
		#write a logging info that an error occured
		return
	PK = (a/k) + ((1-a)/n)
	return PK

def CalacPi(a,n,k,i): 

	if i <= 0 :
		#write a logging info that an error occured
		return

	if i<=k: # the case of the best matches, a higher probability will be given
		PK= CalacPK(a,n,k,i)
		Pi=(PK)/(1-(i-1)*PK)
	
	if i>k: # the case of the less important pods, a lower probability will be given 
		Pi=1/float(n-(i-1))

	return Pi

def CalacK(SEP,options):
	if options['K']==-1: 
		k=1
		for i in range(len(SEP)):
			if SEP[i].lat==SEP[i+1].lat:
				k+=1
			break
		return k 
	return options['K']

def CalacProbFromPod(podprob): #pass the pod probabilities from calacProba to calculate the rules to be applied 
	prob = []
	for i in range(len(podprob)):
		pie = 1 
		if i == 0 : 
			prob.append(podprob[0])
		elif i == len(podprob) - 1 :
			prob.append(1)

		else:
			for p in prob: 
				pie *= (1-p)
			if podprob[i]/pie <1 :
				prob.append(podprob[i]/pie)
			else:
				prob.append(1)
	return prob
