import json
import anytree
import sys
import utils
import context
import match
import refMaps

grayCount1 = 0
grayCount2 = 0

#Context dependent - if this parent->child sub-tree is found, skip the child node. It is an extra node in one of the trees
#TODO: fix this to go child->parent or something else to allow multiple contexts
adlStructMap = dict({"class":"body", "binary":"*", "if":"case"})

'''
Given a node, mark it and all of its children recursivley, until we reach the leaves
'''
def getColor(node):
	if not "tags" in node:
		return refMaps.notMatchedColor		

	parentTags = None
	gpTags = None

	if "parent" in node and "tags" in node["parent"]:
		parentTags = node["parent"]["tags"]

	if "parent" in node and "parent" in node["parent"] and "tags" in node["parent"]["parent"]:
		gpTags = node["parent"]["parent"]["tags"]


	for tag in node["tags"]:
		if tag in refMaps.adlDetailMap and refMaps.adlDetailMap[tag] == context.Context(parentTags, gpTags): 
			return refMaps.adlDetailColor

	return refMaps.notMatchedColor


def markSubtree(node):
	markNode(node, getColor(node))

	if not "children" in node:
		return

	for child in node["children"]:
		markSubtree(child)

'''
Mark a single node
'''
def markNode(node, color):
	if not utils.hasTags(node):
		node["tags"] = []

	node["tags"].append(color)

	#if isFirst:
	#node["tags"].append("#ff0000")
	#else:
	#node["tags"].append("#ffff00")

'''
Given a node and its parent, see if it exists in the structEql map
'''
def inAdlStructMap(parent, node):
	if not utils.hasTags(parent) or not utils.hasTags(node): return False
	
	#print("checking strEql of ", node["tags"], "with parent:", parent["tags"])
	
	for tag in parent["tags"]:
		for tag_ in node["tags"]:
			if (tag.lower() in adlStructMap and 
				(adlStructMap[tag.lower()] == tag_.lower() or adlStructMap[tag.lower()] == "*")):
				return True

	return False


'''
Wrapper around inAdlStructMap
'''
def additionalStructure(node):
	if not "parent" in node or not "tags" in node:
		return False

	return inAdlStructMap(node["parent"], node)

def datasMatch(node, node2):
	return node["data"] == node2["data"]

def typesMatch(node, node2):
	return node["type"] == node2["type"]

def delAddedTags(node):
	if not "matched" in node:
		return 

	del node["parent"]
	del node["matched"]

	if "match" in node:
		del node["match"]

	if not "children" in node:
		return;
	
	for child in node["children"]:
		delAddedTags(child)

def getBestMatch(potentialMatches):
	#print("potentialMatches:")
	#for match in potentialMatches:
	#	print(match[0]["tags"])

	bestConfValue = -1
	bestMatch = None
	for match in potentialMatches:
		if match.confidence > bestConfValue:
			bestMatch = match
			bestConfValue = match.confidence

	return bestMatch



def nodeInSameLevel(nodes):
	for node in nodes:
		if "parent" in node:
			return node
	return None

'''Main recursive function - Occurs in the following steps:
(1) For each node in tree1, find the best matching node in tree2
(2) Check all unmatched nodes to see if they are an "additional structure" node
	-> If there is a better match because of this new found structure, match that instead
(3) Recurse on all matched nodes children
(4) Cleanup Phase: Recurse from the root down to the leaves deleting all of the added tags (Matched and Parent)
'''
def checkChildren(t1Nodes, t2Nodes, parent1, parent2):
	global grayCount1
	global grayCount2

	#add the matched and parent tags
	#TODO - use the utils edit children function
	unEditedNodes = (node for node in t1Nodes if not "matched" in node)
	for node in unEditedNodes:
		node["matched"] = False
		node["parent"] = parent1
	unEditedNodes = (node for node in t2Nodes if not "matched" in node)
	for node2 in unEditedNodes:
		node2["matched"] = False
		node2["parent"] = parent2


	'''
	Step (1) - Find a match in tree2 for each node in tree1

	'''
	for node in t1Nodes:	
		potentialMatches = utils.getAllPotentialMatches(node, t2Nodes)
		bestMatch = getBestMatch(potentialMatches)	
		if not node["matched"] and not bestMatch == None:
			utils.matchNodes(node, bestMatch.node, bestMatch.confidence)	

		
	
	'''
	Step (2) - Check all unmatched nodes for a additional structure node
	'''
	unmatchedNodes = (node for node in t1Nodes if not node["matched"])
	for node in unmatchedNodes:
		if additionalStructure(node):
			node["matched"] = True

			node["match"] = None

			markNode(node, refMaps.adlStrColor)

			print(node["tags"], "is an additional strucutre")

			'''
			See if there is a better match based on the additional structure
			'''

			for node2 in t2Nodes:
				utils.editChildren(node)
				potentialMatches = utils.getAllPotentialMatches(node2, node["children"])
				bestMatch = getBestMatch(potentialMatches)	
				if not bestMatch == None and bestMatch.confidence > node2["match"].confidence:
					utils.unMatchNode(node2["match"].node)
					utils.matchNodes(node2, bestMatch.node, bestMatch.confidence)
					
			

	'''
	unmatchedNodes2 = (node2 for node2 in t2Nodes if not node2["matched"])
	for node2 in unmatchedNodes:
		print("checking if", node2["tags"], "is an additional struct")
		if additionalStructure(node2):
			node2["matched"] = True
			markNode(node2, False)
			print("struct eql2")
			#recurse with the numatched node, and a tree1 node from the current level
			checkChildren(node["parent"]["children"], node2["children"], node["parent"], node2)
		#else: markSubtree(node2, False)
	'''

	'''
	Step (3) Recurse on all matched nodes children
	'''
	matchedNodes = (node for node in t1Nodes if node["matched"])
	for node in matchedNodes:
		if node["match"] == None: #At an adl structure node
			node2 = nodeInSameLevel(t2Nodes)
			checkChildren(node["children"], node2["parent"]["children"], node, node2["parent"])
			continue

		node2 = node["match"].node
		if "children" in node and "children" in node2:
			checkChildren(node["children"], node2["children"], node, node2)



	'''
	Step (4) Cleanup Phase
	'''

	unmatchedNodes = (node for node in t1Nodes if not node["matched"])
	for node in unmatchedNodes:
		markSubtree(node)		

	unmatchedNodes = (node2 for node2 in t2Nodes if not node2["matched"])
	for node2 in unmatchedNodes:
		markSubtree(node2)	

	#grayCount1+=1 for all matchedNodes

def runner():
	if len(sys.argv) < 3:
		print("error: must specify two files")
		exit()

	with open(sys.argv[1], 'r') as f:
			jsonObj1 = json.load(f)

	with open(sys.argv[2], 'r') as f:
		jsonObj2 = json.load(f)

	if not utils.hasTags(jsonObj1) or not utils.hasTags(jsonObj2):
		print("error: illformatted json doesn't have tags")
	elif not utils.tagsMatch(jsonObj1, jsonObj2, None, None):
		print("error: root nodes don't match")
	else:
		checkChildren(jsonObj1["children"], jsonObj2["children"], jsonObj1, jsonObj2)
		if not grayCount1 == grayCount2:
			print("error: number of gray nodes in each graph is not equal. We have a problem")

		for child in jsonObj1["children"]:
			delAddedTags(child)

		for child in jsonObj2["children"]:
			delAddedTags(child)


		#output to a new file
		index1 = sys.argv[1].rfind(".")
		index2 = sys.argv[2].rfind(".")

		with open(sys.argv[1][0:index1] + "Modified.json", "w+") as fw:
			fw.write(json.dumps(jsonObj1))
		
		with open(sys.argv[2][0:index2] + "Modified.json", "w+") as fw:
			fw.write(json.dumps(jsonObj2))
runner()
