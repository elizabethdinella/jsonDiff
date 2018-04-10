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


#Context independent equality - (Tag1 always == Tag2 and Tag2 always == Tag1 regardless of context)
tagEqualityMap = dict({"ClassDef": "class", "FunctionDef": "function", "CompoundStmt": "body"})

#context dependent equality - (Tag1 always == Tag2 in the context A)

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


#def structuralEquality(node):''', node2'''
def structuralEquality(node):


	#if not "parent" in node: '''or not "parent" in node2'''
	if not "parent" in node:
		return False

	#for the print 
	#if not "tags" in node: '''or not "tags" in node2'''
	if not "tags" in node: 
		return False

	node1Str = False
	node2Str = False
	if inStructEqlMap(node["parent"], node):
		node1Str = True
		#elif inStructEqlMap(node2["parent"], node2):
		#node2Str = True'
	else:
		return False

	'''
	if tagsMatch(node["parent"], node2["parent"]):
		if node1Str: node["matched"] = True
		else: node2["matched"] = True
		
		return True

	return False	
	'''

	return True


def equalTags(tag, tag_):
	if tag.lower() == tag_.lower():
		return True
	elif (tag in tagEqualityMap and tagEqualityMap[tag] == tag_):
		return True
	elif (tag_ in tagEqualityMap and tagEqualityMap[tag_] == tag):
		return True
	else:
		return False
			

def tagsMatch(tags1, tags2):
	for tag in tags1:
		for tag_ in tags2:
			if equalTags(tag, tag_ ):
				return True

	return False;

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
			if((hasTags(node) and hasTags(node2) and tagsMatch(node["tags"], node2["tags"]) and not node2["matched"]) or 
				(not hasTags(node) and not hasTags(node2) and typesMatch(node, node2) and datasMatch(node, node2))):

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

	for node in t1Nodes:
		strEql = False
		if not node["matched"]:
			strEql = False
			if structuralEquality(node):
				markNode(node, True)
				strEql = True
				print("struct eql")
				checkChildren(node["children"], node2["parent"]["children"], node, node2["parent"])

			if not strEql: markSubtree(node, True)
		else:
			grayCount1+=1
		

	'''
	for node in t1Nodes:
		if not node["matched"]:
			strEql = False
			for node2 in t2Nodes:
				if not node2["matched"] and structuralEquality(node, node2):
					markNode(node, True)
					strEql = True
					print("struct eql")

					#if "children" in node and "children" in node2: 
					if node["matched"]:
						checkChildren(node["children"], node2["parent"]["children"], node, node2["parent"])
					break
					#if there is structual equality then we need to skip a level 
				
			if not strEql: markSubtree(node, True)
		else:
			grayCount1 += 1
	'''
			
	
	for node in t2Nodes:
		if not node["matched"]:
			strEql = False
			for node2 in t1Nodes:
				'''
				if not node2["matched"] and structuralEquality(node, node2):
					markNode(node, False)
					strEql = True
					print("struct eql")
					break
				'''

			if not strEql: markSubtree(node, False)
		else:
			grayCount2 += 1



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
	elif not tagsMatch(jsonObj1["tags"], jsonObj2["tags"]):
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
