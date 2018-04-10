import json
import anytree
import sys

grayCount1 = 0
grayCount2 = 0

'''
TODO: change this equality map to allow for more than two languages 

- we have tag equality and structural equality. structural equality means that we mark just the node but not the whole subtree. In the structural equality map we have tuples. If (parent, child) is in the map, and the parents are equal than mark the node.

	The flow is that we check for tag equality. If there is not tag equality, then we check for structural equality, mark the node, and move	 on
'''

class Context:
	def __init__(self, parentTags):
		self.parentTags = parentTags

	def __eq__(self, other):
		for tag in self.parentTags:
			for tag_ in other.parentTags:
				if tag.lower() == tag_.lower():
					return True
		return False

#NOTE: everything in these maps must be ALL lowercase

#Context independent equality - (Tag1 always == Tag2 and Tag2 always == Tag1 regardless of context)
tagEqualityMap = dict({"classdef": "class", "functiondef": "function", "compoundstmt": "body"})

#context dependent equality - (Tag1 always == Tag2 in the context A)
tagEqlMap2 = dict({"case":("compoundstmt", Context(["if"])), "else":("compoundstmt", Context(["if"]))})

#Context dependent - if this parent->child sub-tree is found, skip the child node. It is an extra node in one of the trees
structEqlMap = dict({"class":"body"})

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
	if not hasTags(node):
		node["tags"] = []

	if isFirst:
		node["tags"].append("#ff0000")
	else:
		node["tags"].append("#ffff00")


'''
Given a node and its parent, see if it exists in the structEql map
'''
def inStructEqlMap(parent, node):
	if not hasTags(parent) or not hasTags(node): return False
	
	for tag in parent["tags"]:
		for tag_ in node["tags"]:
			if tag in structEqlMap and structEqlMap[tag] == tag_:
				return True

	return False


'''
Wrapper around inStructEqlMap
'''
def structuralEquality(node):
	if not "parent" in node or not "tags" in node:
		return False

	return inStructEqlMap(node["parent"], node)

'''
Checks if two tags are equal using the equality map
'''
def equalTags(tag, tag_):
	if tag.lower() == tag_.lower():
		return True
	elif (tag.lower() in tagEqualityMap and tagEqualityMap[tag.lower()] == tag_.lower()):
		return True
	elif (tag_.lower() in tagEqualityMap and tagEqualityMap[tag_.lower()] == tag.lower()):
		return True
	else:
		return False


def equalContextTags(tag, tag_, parent1Tags, parent2Tags):
	if (tag.lower() in tagEqlMap2 and tagEqlMap2[tag.lower()][0] == tag_.lower() 
		and tagEqlMap2[tag.lower()][1] == Context(parent1Tags)):
			return True

	if (tag_.lower() in tagEqlMap2 and tagEqlMap2[tag_.lower()][0] == tag.lower()
		and tagEqlMap2[tag_.lower()][1] == Context(parent2Tags)):
			return True

	return False
			
'''
Given two nodes, check if any tags are equal
'''
def tagsMatch(tags1, tags2, parent1Tags, parent2Tags):
	for tag in tags1:
		for tag_ in tags2:
			if equalTags(tag, tag_ ):
				return True
	for tag in tags1:
		for tag_ in tags2:
			if equalContextTags(tag, tag_, parent1Tags, parent2Tags):
				print("equal context!")
				return True
	return False

def hasTags(node):
	return "tags" in node 

def datasMatch(node, node2):
	return node["data"] == node2["data"]

def typesMatch(node, node2):
	return node["type"] == node2["type"]

def delAddedTags(node):
	if not "matched" in node:
		return 

	del node["parent"]
	del node["matched"]

	if not "children" in node:
		return;
	
	for child in node["children"]:
		delAddedTags(child)

def nodesMatch(node, node2, parent, parent2):
	return ((hasTags(node) and hasTags(node2) and 
		tagsMatch(node["tags"], node2["tags"], parent["tags"], parent2["tags"]) and not node2["matched"]) 
		or (not hasTags(node) and not hasTags(node2) and typesMatch(node, node2) and datasMatch(node, node2)))


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
	for node in t1Nodes:
		node["matched"] = False
		node["parent"] = parent1
	for node in t2Nodes:
		node["matched"] = False
		node["parent"] = parent2


	'''
	First recursion - Find a match in tree2 for each node in tree1

	'''
	for node in t1Nodes:	
		for node2 in t2Nodes:
			if nodesMatch(node, node2, parent1, parent2):		
				node["matched"] = True
				node2["matched"] = True

				#If there is a match, we recurse on the children
				if "children" in node and "children" in node2:
					checkChildren(node["children"], node2["children"], node, node2)
				break

	'''
	Second recurion - On the way up, check for structural equality 
			(a node level that exists in one tree but not the other)

	
	'''
	unmatchedNodes = (node for node in t1Nodes if not node["matched"])
	for node in unmatchedNodes:
		if structuralEquality(node):
			node["matched"] = True
			markNode(node, True)
			print("struct eql")
			#recurse with the unmatched node, and a tree2 node from the current level
			checkChildren(node["children"], node2["parent"]["children"], node, node2["parent"])
		#else: markSubtree(node, True)




	unmatchedNodes = (node2 for node2 in t2Nodes if not node2["matched"])
	for node2 in unmatchedNodes:
		if structuralEquality(node2):
			node2["matched"] = True
			markNode(node2, False)
			print("struct eql")
			#recurse with the numatched node, and a tree1 node from the current level
			checkChildren(node["parent"]["children"], node2["children"], node["parent"], node2)
		#else: markSubtree(node2, False)


	unmatchedNodes = (node for node in t1Nodes if not node["matched"])
	for node in unmatchedNodes:
		markSubtree(node, True)		

	unmatchedNodes = (node2 for node2 in t2Nodes if not node2["matched"])
	for node2 in unmatchedNodes:
		markSubtree(node2, False)	


	#grayCount1+=1 for all matchedNodes

def runner():
	if len(sys.argv) < 3:
		print("error: must specify two files")
		exit()

	with open(sys.argv[1], 'r') as f:
    		jsonObj1 = json.load(f)

	with open(sys.argv[2], 'r') as f:
		jsonObj2 = json.load(f)

	if not hasTags(jsonObj1) or not hasTags(jsonObj2):
		print("error: illformatted json doesn't have tags")
	elif not tagsMatch(jsonObj1["tags"], jsonObj2["tags"], None, None):
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
