import json
import anytree
import sys
import utils
import context
import match
import refMaps

printAdlDetail = False
printAdlStr = False

matched1 = 0
matched2 = 0
adlStr1 = 0
adlStr2 = 0
adlDetail1 = 0
adlDetail2 = 0
unmatched1 = 0
unmatched2 = 0

'''
Given a node, mark it and all of its children recursivley, until we reach the leaves
'''
def getColor(node):
	if not "tags" in node:
		return refMaps.notMatchedColor		

	for tag in node["tags"]:
		if tag.lower() in refMaps.adlDetailMap:
			for cntxt in refMaps.adlDetailMap[tag.lower()]:
				if cntxt == utils.createContext(node): 
					if printAdlDetail: print(node["tags"], "is an additional detail")
					return refMaps.adlDetailColor

	return refMaps.notMatchedColor


def markSubtree(node, color):
	markNode(node, color)

	if not "children" in node:
		return

	utils.editChildren(node)
	for child in node["children"]:
		markSubtree(child, color)


def markAllNodes(nodes):
	unmatchedNodes = (node for node in nodes if (not "matched" in node or (not node["matched"])))
	for node in unmatchedNodes:
		if utils.additionalStructure(node): continue
		color = getColor(node)
		markSubtree(node, color)


	matchedNodes = (node for node in nodes if ("matched" in node and node["matched"]))
	for node in matchedNodes:
		if "children" in node: 
			markAllNodes(node["children"])

'''
Mark a single node
'''
def markNode(node, color):
	if not utils.hasTags(node):
		return

	if not color in node["tags"]:
		node["tags"].append(color)


def datasMatch(node, node2):
	return node["data"] == node2["data"]

def typesMatch(node, node2):
	return node["type"] == node2["type"]

def delAddedTags(node, first):
	global matched1
	global matched2
	global adlStr1
	global adlStr2
	global adlDetail1
	global adlDetail2
	global unmatched1
	global unmatched2

	if first:
		if "tags" in node and refMaps.adlDetailColor in node["tags"]: adlDetail1 += 1
		elif "tags" in node and refMaps.adlStrColor in node["tags"]: adlStr1 += 1
		elif "tags" in node and refMaps.notMatchedColor in node["tags"]: unmatched1 += 1
		elif "tags" in node: matched1 += 1
	else:
		if "tags" in node and refMaps.adlDetailColor in node["tags"]: adlDetail2 += 1
		elif "tags" in node and refMaps.adlStrColor in node["tags"]: adlStr2 += 1
		elif "tags" in node and refMaps.notMatchedColor in node["tags"]: unmatched2 += 1
		elif "tags" in node: matched2 += 1


	if not "matched" in node:
		return 

	del node["parent"]
	del node["matched"]

	if "match" in node:
		del node["match"]

	if not "children" in node:
		return;
	
	for child in node["children"]:
		delAddedTags(child, first)

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


	for node2 in t2Nodes:
		if utils.additionalStructure(node2):
			if "match" in node2 and not node2["match"] == None: utils.unMatchNode(node2["match"].node)
			node2["matched"] = True
			node2["match"] = None

			markNode(node2, refMaps.adlStrColor)

			if printAdlStr: print(node2["tags"], "is an additional strucutre")


	'''
	Step (1) - Find a match in tree2 for each node in tree1

	'''
	for node in t1Nodes:	
		if utils.additionalStructure(node):
			node["matched"] = True
			node["match"] = None
			markNode(node, refMaps.adlStrColor)
			if printAdlStr: print(node["tags"], "is an additional strucutre")

		else:
			potentialMatches = utils.getAllPotentialMatches(node, t2Nodes)
			bestMatch = getBestMatch(potentialMatches) #should give an index
			if not node["matched"] and not bestMatch == None:
				utils.matchNodes(node, bestMatch.node, bestMatch.confidence)

	matchedNodes = (node for node in t1Nodes if node["matched"])
	for node in matchedNodes:
		if utils.additionalStructure(node) and "children" in node: 
			#print("recursing with the children of", node["tags"], "and t2nodes")
			checkChildren(node["children"], t2Nodes, node, parent2)
		else:
			node2 = node["match"].node
			#print("recursing with the children of", node["tags"], "and", node2["tags"])
			if "children" in node and "children" in node2:
				checkChildren(node["children"], node2["children"], node, node2)

	
def runner():
	if len(sys.argv) < 3:
		print("error: must specify two files")
		exit()

	with open(sys.argv[1], 'r') as f:
			jsonObj1 = json.load(f)

	with open(sys.argv[2], 'r') as f:
		jsonObj2 = json.load(f)


	reportf = open(sys.argv[3], 'a')

	if not utils.hasTags(jsonObj1) or not utils.hasTags(jsonObj2):
		print("error: illformatted json doesn't have tags")
	elif not utils.tagsMatch(jsonObj1, jsonObj2, None, None):
		print("error: root nodes don't match")
	else:
		checkChildren(jsonObj1["children"], jsonObj2["children"], jsonObj1, jsonObj2)
		#if not grayCount1 == grayCount2:
		#	print("error: number of gray nodes in each graph is not equal. We have a problem")

		
		markAllNodes(jsonObj1["children"])
		markAllNodes(jsonObj2["children"])
	

		for child in jsonObj1["children"]:
			delAddedTags(child, True)

		for child in jsonObj2["children"]:
			delAddedTags(child, False)


		#output to a new file
		index1 = sys.argv[1].rfind(".")
		index2 = sys.argv[2].rfind(".")

		with open(sys.argv[1][0:index1] + "Modified.json", "w+") as fw:
			fw.write(json.dumps(jsonObj1))
		
		with open(sys.argv[2][0:index2] + "Modified.json", "w+") as fw:
			fw.write(json.dumps(jsonObj2))

		totalNodes1 = matched1 + unmatched1 + adlStr1 + adlDetail1
		totalNodes2 = matched2 + unmatched2 + adlStr2 + adlDetail2

		reportf.write("\n\n\nfile: " + sys.argv[1][0:index1] + "\n\ttotal nodes:" + str(totalNodes1) + "\n\tnum unmatched nodes: " 
				+ str(unmatched1) + "\n\tnum matched nodes: " + str(matched1) + "\n\tadl struct nodes: " + str(adlStr1)
				+ "\n\tadl detail nodes: " + str(adlDetail1) + "\n\n"
				+ "file: " + sys.argv[2][0:index2] + "\n\ttotal nodes:" + str(totalNodes2) + "\n\tnum unmatched nodes: " 
				+ str(unmatched2) + "\n\tnum matched nodes: " + str(matched2) + "\n\tadl struct nodes: " + str(adlStr2)
				+ "\n\tadl detail nodes: " + str(adlDetail2) + "\n")
runner()
