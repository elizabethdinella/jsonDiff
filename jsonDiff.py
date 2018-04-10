import json
import anytree
import sys

grayCount1 = 0
grayCount2 = 0

'''
change this equality map to allow for more than two languages 
and allow structure
ideas for allowing structure: 
- just pass the parent tag as well as the current tag when checking for equality
- create a function for checking equality. Don't just check tags. Pass in a node and we can check for any structural things as long as we have a pointer back to the parent.

- we have tag equality and structural equality. structural equality means that we mark just the node but not the whole subtree. In the structural equality map we have tuples. If (parent, child) is in the map, and the parents are equal than mark the node.

	The flow is that we check for tag equality. If there is not tag equality, then we check for structural equality, mark the node, and move	 on
'''


tagEqualityMap = dict({"ClassDef": "class", "FunctionDef": "function"})

#parent->child
structEqlMap = dict({"class":"body"})


def markSubtree(node, isFirst):
	markNode(node, isFirst)

	if not "children" in node:
		return

	for child in node["children"]:
		markSubtree(child, isFirst)

def markNode(node, isFirst):
	if not hasTags(node):
		node["tags"] = []

	if isFirst:
		node["tags"].append("#ff0000")
	else:
		node["tags"].append("#ffff00")


def inStructEqlMap(key, value):
	if not hasTags(key) or not hasTags(value): return False
	
	for tag in key["tags"]:
		for tag_ in value["tags"]:
			if tag in structEqlMap and structEqlMap[tag] == tag_:
				return True

	return False


def structuralEquality(node, node2):

	if not "parent" in node or not "parent" in node2:
		return False

	#for the print 
	if not "tags" in node or not "tags" in node2:
		return False

	node1Str = False
	node2Str = False
	if inStructEqlMap(node["parent"], node):
		node1Str = True
	elif inStructEqlMap(node2["parent"], node2):
		node2Str = True
	else:
		return False

	if tagsMatch(node["parent"], node2["parent"]):
		if node1Str: node["matched"] = True
		else: node2["matched"] = True
		
		return True

	return False	


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

def checkChildren(t1Nodes, t2Nodes, parent1, parent2):
	global grayCount1
	global grayCount2

	for node in t1Nodes:
		node["matched"] = False
		node["parent"] = parent1
	for node in t2Nodes:
		node["matched"] = False
		node["parent"] = parent2


	#Find a matching node from tree2 for each node tree1
	for node in t1Nodes:	
		for node2 in t2Nodes:
			if((hasTags(node) and hasTags(node2) and tagsMatch(node["tags"], node2["tags"]) and not node2["matched"]) or 
				(not hasTags(node) and not hasTags(node2) and typesMatch(node, node2) and datasMatch(node, node2))):

				node["matched"] = True
				node2["matched"] = True

				if "children" in node and "children" in node2:
					checkChildren(node["children"], node2["children"], node, node2)
				break
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
