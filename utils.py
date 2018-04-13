import refMaps
import context
import match 

def hasTags(node):
	return "tags" in node 

def matchNodes(node1, node2, conf):
	node1["matched"] = True
	node2["matched"] = True
	node1["match"] = match.Match(node2, conf)
	node2["match"] = match.Match(node1, conf)


def unMatchNode(node):
	node["match"] = None
	node["matched"] = False

def findMultTags(tags):
	multTags = []
	for tag in tags:
		if tag == None: continue
		if tag[0] == "+" and len(tag) > 1:
			multTags.append(tag[1:])
	return multTags

def findDenyTags(tags):
	denyTags = []
	for tag in tags:
		if tag == None: continue
		if tag[0] == "!":
			denyTags.append(tag[1:])

	return denyTags


'''
Given two nodes, check if any tags are equal
'''
def tagsMatch(node1, node2, parent1, parent2):
	tags1 = node1["tags"]
	tags2 = node2["tags"]
	
	deny = findDenyTags(tags1) + findDenyTags(tags2)
	mult = findMultTags(tags1) + findMultTags(tags2)
	if len(deny) > 0: print("deny tags:", deny)
	if len(mult) > 0: print("mult tags:", mult)

	multCount1 = 0 
	multCount2 = 0
	
	
	#check if the tags are naively equal
	for tag in tags1:
		if len(deny) > 0: print(tag, "in deny?", tag in deny)
		if tag == "*": return 1
		if tag in deny: return -1
		if tag in mult: multCount1 += 1
		for tag_ in tags2:
			if tag_ == "*": return 1
			if tag_ in deny: return -1
			if tag_ in mult: mult2Count += 1
			if tag.lower() == tag_.lower() and len(mult) == 0:
				return 1

		if len(deny) > 0: return 1

	if len(mult) > 0 and multCount1 > 1 or multCount2 > 1: return 1
	elif len(mult) > 0: return -1

	confidence1 = equalTags(node1, node2, parent1, parent2) 
	if not confidence1 == -1:
		return confidence1

	return equalTags(node2, node1, parent2, parent1)

def cntxtInsensitiveCheck(eqObj, tags2):
	for tag_ in eqObj.tags:
		if not tag_.lower() in tags2:
			return False
	return True

def confidenceOfMatch(node, node2, parent, parent2):
	if hasTags(node) and hasTags(node2): #and not node2["matched"]:
		confidence1 = tagsMatch(node, node2, parent, parent2)
		if not confidence1 == -1:
			return confidence1
		elif not hasTags(node) and not hasTags(node2) and typesMatch(node, node2) and datasMatch(node, node2): return 1

	return -1


def getAllPotentialMatches(node, t2Nodes):
	potentialMatches = []
	unmatchedNodes = (node for node in t2Nodes if not node["matched"])
	for node2 in unmatchedNodes:
		confidence = confidenceOfMatch(node, node2, node["parent"], node2["parent"]) 
		if not confidence == -1:
			potentialMatches.append(match.Match(node2, confidence))

	return potentialMatches

def editChildren(node):
	for child in node["children"]:
		if not "parent" in child: child["parent"] = node
		if not "matched" in child: child["matched"] = False		

def calculateConfidence(node1, node2, level):
	print("calculating confidence of matching", node1["tags"], "and", node2["tags"])
	numMatch = 0 
	if "children" in node1 and "children" in node2:
		editChildren(node1)
		editChildren(node2)

		for child in node1["children"]:
			child["parent"] = node1
			numMatch += len(getAllPotentialMatches(child, node2["children"]))
		print("confidence: ", numMatch / len(node1["children"]))
		return numMatch / len(node1["children"])

	return 0


'''
Checks if two tags are equal using the equality map
'''
def equalTags(node1, node2, parent1, parent2):
	tags1 = node1["tags"]
	tags2 = node2["tags"]

	#if it is a key in the equality map with an empty context
	for tag in tags1:
		if tag.lower() in refMaps.tagEqlMap:
			for eqObj in refMaps.tagEqlMap[tag.lower()]:
				if eqObj.context == context.Context() and cntxtInsensitiveCheck(eqObj, tags2): return 1
				elif cntxtInsensitiveCheck(eqObj, tags2) and contextSensitiveCheck(eqObj, node1, parent1):  
					return calculateConfidence(node1, node2, 1)
					print("context sensitive match!")
	return -1

def createContext(node):
	lookaheadTags = None
	siblingTags = None
	parentTags = None
	gpTags = None

	if "children" in node:
		lookaheadTags = []
		for child in node["children"]:
			if "tags" in child:
				lookaheadTags += child["tags"]

	if not lookaheadTags == None and len(lookaheadTags) == 0:
		lookaheadTags = None

	if "parent" in node and "children" in node["parent"]:
		siblingTags = []
		for child in node["parent"]["children"]:
			if "tags" in child and not child == node:
				siblingTags += child["tags"]

	if not siblingTags == None and len(siblingTags) == 0:
		siblingTags = None

	if "parent" in node and "tags" in node["parent"]:
		parentTags = node["parent"]["tags"]


	if "parent" in node and "parent" in node["parent"] and "tags" in node["parent"]["parent"]:
		gpTags = node["parent"]["parent"]["tags"]

	return context.Context(lookaheadTags, siblingTags, parentTags, gpTags)

def contextSensitiveCheck(eqObj, node1, parent1):
	return eqObj.context == createContext(node1)


def levelUp(tag, parent2):
	if tag == "binary": print("checking level up of", tag, "and", parent2)

	if parent2 == None: return False
	if tag.lower() in refMaps.tagEqlMap and "*" in refMaps.tagEqlMap[tag.lower()][0]: print("checking level up of", tag, "and", parent2)
	for ptag in parent2:
		if(tag.lower() in refMaps.tagEqlMap and "*" in refMaps.tagEqlMap[tag.lower()][0] and ptag in refMaps.tagEqlMap[tag.lower()][0]): return True

	return False



