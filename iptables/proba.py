#This file will contain the probability equations used with the iptables.
#The probability of the rule #i is equal to pi, however these probabilities dosen't reflect the probability of accessing the pods.
#Pi is the probability of acheiving the rule, which means that the probability of accessing the pod is equal to the probability of the current rules multiplied by the probabilities of not taking the previous rules. 
#a is alpha variable, selected by the user using the arguments, and it reflects the importance in proximity. 
#n is the number of the pod in the replicaset. 
#k is the number of prefered pods over the others according to latency. 
#i is the index of the rule/pod.
#PK is the probability of the first rule. 

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

def CalacK(SEP): 
	k=1
	for i in range(len(SEP)):
		if SEP[i].lat==SEP[i+1].lat:
			k+=1
		break
	return k 