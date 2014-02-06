def resultLengthRDF(l):
	return len(l)

def subjectRDF(rt):
	return rt[0][0]

def predicateRDF(rt):
	return rt[0][1]

def objectRDF(rt):
	return rt[0][2]

# Use only for query results! 
def tripleObjectType(rt):
	return rt[1]


def subjectsRDF(rl):
	r = []
	for i in rl:
		r.append(subjectRDF(i))
	return r

def predicatesRDF(rl):
	r = []
	for i in rl:
		r.append(predicateRDF(i))
	return r

def objectsRDF(rl):
	r = []
	for i in rl:
		r.append(objectRDF(i))
	return r

def resultLengthWQL(l):
	return len(l)

def getValuesByWQL(s,p,q):
	#s is a subject
	#p is a predicate
	#q is some query transaction
	r = q.wql_values_query((s, False), "['seq', "+p+"]")
	return r
	
def getValuesByRDF(obj, q):
	r_tmp = q.rdf_query(((obj, None, None), 'literal'))
	r = [i[0][2] for i in r_tmp]
