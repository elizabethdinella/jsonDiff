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

'''
Given two nodes, check if any tags are equal
'''
def tagsMatch(node1, node2, parent1, parent2):
	tags1 = node1["tags"]
	tags2 = node2["tags"]

	#check if the tags are naively equal
	for tag in tags1:
		if tag == "*": return True
		for tag_ in tags2:
			if tag_ == "*": return True
			if tag.lower() == tag_.lower():
				return True

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
	for node2 in t2Nodes:
		confidence = confidenceOfMatch(node, node2, node["parent"], node2["parent"]) 
		if not confidence == -1:
			potentialMatches.append(match.Match(node2, confidence))

	return potentialMatches

def editChildren(node):
	for child in node["children"]:
		child["parent"] = node
		child["matched"] = False		

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
				elif cntxtInsensitiveCheck(eqObj, tags2) and contextSensitiveCheck(eqObj, parent1):  
					return calculateConfidence(node1, node2, 1)
					print("context sensitive match!")
	return -1

def contextSensitiveCheck(eqObj, parent1):

	parentTags = None
	gpTags = None


	if not parent1  == None:
		if "tags" in parent1:
			parentTags = parent1["tags"]

		if "parent" in parent1 and "tags" in parent1["parent"]:
			gpTags = parent1["parent"]["tags"]

	return eqObj.context == context.Context(parentTags, gpTags)


def levelUp(tag, parent2):
	if tag == "binary": print("checking level up of", tag, "and", parent2)

	if parent2 == None: return False
	if tag.lower() in refMaps.tagEqlMap and "*" in refMaps.tagEqlMap[tag.lower()][0]: print("checking level up of", tag, "and", parent2)
	for ptag in parent2:
		if(tag.lower() in refMaps.tagEqlMap and "*" in refMaps.tagEqlMap[tag.lower()][0] and ptag in refMaps.tagEqlMap[tag.lower()][0]): return True

	return False



