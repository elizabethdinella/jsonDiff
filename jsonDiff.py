import json
import anytree
import sys
import utils
import context
import match

grayCount1 = 0
grayCount2 = 0

'''
TODO: change this equality map to allow for more than two languages 

- we have tag equality and structural equality. structural equality means that we mark just the node but not the whole subtree. In the structural equality map we have tuples. If (parent, child) is in the map, and the parents are equal than mark the node.

	The flow is that we check for tag equality. If there is not tag equality, then we check for structural equality, mark the node, and move	 on
'''

#Context dependent - if this parent->child sub-tree is found, skip the child node. It is an extra node in one of the trees
#TODO: fix this to go child->parent or something else to allow multiple contexts
adlStructMap = dict({"class":"body", "binary":"*", "if":"case"})

'''
Given a node, mark it and all of its children recursivley, until we reach the leaves
'''
def markSubtree(node, isFirst):
	markNode(node, isFirst)

	if not "children" in node:
		return

	for child in node["children"]:
		markSubtree(child, isFirst)

'''
Mark a single node
'''
def markNode(node, isFirst):
	if not utils.hasTags(node):
		node["tags"] = []

	if isFirst:
		node["tags"].append("#ff0000")
	else:
		node["tags"].append("#ffff00")


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

'''Main recursive function - Three recursions occur:
(1) Recurses down the tree to find nodes with context independent tag matching
(2) On the way back up from (1), looks for structural equality. 
	-> If found, recurse down again on that node
(3) Recurse from the root down to the leaves deleting all of the added tags (Matched and Parent)
'''
def checkChildren(t1Nodes, t2Nodes, parent1, parent2):
	global grayCount1
	global grayCount2

	#add the matched and parent tags
	unEditedNodes = (node for node in t1Nodes if not "matched" in node)
	for node in unEditedNodes:
		node["matched"] = False
		node["parent"] = parent1
	unEditedNodes = (node for node in t2Nodes if not "matched" in node)
	for node2 in unEditedNodes:
		node2["matched"] = False
		node2["parent"] = parent2


	'''
	First recursion - Find a match in tree2 for each node in tree1

	'''
	for node in t1Nodes:	
		potentialMatches = utils.getAllPotentialMatches(node, t2Nodes)
		bestMatch = getBestMatch(potentialMatches)	
		if not node["matched"] and not bestMatch == None:
			node2 = bestMatch.node
			node["matched"] = True
			node2["matched"] = True
			node["match"] = bestMatch
			node2["match"] = match.Match(node, bestMatch.confidence)

			'''
			#dont do this yet!
			#If there is a match, we recurse on the children
			if "children" in node and "children" in node2:
				checkChildren(node["children"], node2["children"], node, node2)
			#break'''
		
	
	'''
	Second recurion - On the way up, check for structural equality 
			(a node level that exists in one tree but not the other)

	
	'''
	unmatchedNodes = (node for node in t1Nodes if not node["matched"])
	for node in unmatchedNodes:
		print("checking if", node["tags"], "is an additional struct")
		if additionalStructure(node):
			node["matched"] = True
			node["match"] = None
			markNode(node, True)
			print(node["tags"], "is an additional strucutre")
			#recurse with the unmatched node, and a tree2 node from the current level
			'''node2 = nodeInSameLevel(t2Nodes)'''
			#if we've reached the end of one of the trees
			#Maybe don't do this yet
			for node2 in t2Nodes:
				utils.editChildren(node)
				potentialMatches = utils.getAllPotentialMatches(node2, node["children"])
				bestMatch = getBestMatch(potentialMatches)	
				if not bestMatch == None and bestMatch.confidence > node2["match"].confidence:
					node2["match"].node["match"] = None
					node2["match"].node["matched"] = False
					
					node2["match"] = bestMatch
					bestMatch.node["match"] = match.Match(node2, bestMatch.confidence)
					

			'''
			if not node2 == None:
				print("recursing on its children")
				checkChildren(node["children"], node2["parent"]["children"], node, node2["parent"])
			'''
		#else: markSubtree(node, True)

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

	matchedNodes = (node for node in t1Nodes if node["matched"] and not node["match"] == None)
	for node in matchedNodes:
		node2 = node["match"].node
		if "children" in node and "children" in node2:
			checkChildren(node["children"], node2["children"], node, node2)



	unmatchedNodes = (node for node in t1Nodes if not node["matched"])
	for node in unmatchedNodes:
		markSubtree(node, True)		
		#markNode(node, True)

	unmatchedNodes = (node2 for node2 in t2Nodes if not node2["matched"])
	for node2 in unmatchedNodes:
		markSubtree(node2, False)	
		#markNode(node2, False)

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
