import refMaps
import context

'''
Given two nodes, check if any tags are equal
'''
def tagsMatch(tags1, tags2, parent1, parent2):

	#check if the tags are naively equal
	for tag in tags1:
		if tag == "*": return True
		for tag_ in tags2:
			if tag_ == "*": return True
			if tag.lower() == tag_.lower():
				return True

	if equalTags(tags1, tags2, parent1, parent2) or equalTags(tags2, tags1, parent1, parent2):
		return True
	
	return False

'''
Checks if two tags are equal using the equality map
'''
def equalTags(tags1, tags2, parent1, parent2):
	
	for tag in tags1: #loop through each tag
		if tag == "*": return True

		#if it is a key in the equality map with an empty context
		if tag.lower() in refMaps.tagEqlMap and refMaps.tagEqlMap[tag.lower()][1] == context.Context():
			for tag_ in refMaps.tagEqlMap[tag.lower()][0]: #make sure the matching node has all of the nodes in the map
				if not tag_.lower() in tags2:
					return False
			return True
		elif tag.lower() in refMaps.tagEqlMap: #non empty context
			print("checking context")
			for tag_ in tags2:
				if equalContextTagsWrapper(tag, tag_, parent1, parent2):
					print("eql context")
				return equalContextTagsWrapper(tag, tag_, parent1, parent2)
	return False

def equalContextTagsWrapper(tag, tag_, parent1, parent2):

	parent1Tags = None
	parent2Tags = None
	grandParent1Tags = None
	grandParent2Tags = None
	
	if not parent1  == None:
		if "tags" in parent1:
			parent1Tags = parent1["tags"]

		if "parent" in parent1 and "tags" in parent1["parent"]:
			grandParent1Tags = parent1["parent"]["tags"]

	if not parent2 == None:
		if "tags" in parent2:
			parent2Tags = parent2["tags"]
	
		if "parent" in parent2 and "tags" in parent2["parent"]:
			grandParent2Tags = parent2["parent"]["tags"]


	return equalContextTags(tag, tag_, parent1Tags, parent2Tags, grandParent1Tags, grandParent2Tags)

def equalContextTags(tag, tag_, parent1Tags, parent2Tags, grandParent1Tags, grandParent2Tags):
	if (tag.lower() in refMaps.tagEqlMap and tag_.lower() in refMaps.tagEqlMap[tag.lower()][0]):
		print("checking eqlContext of ", tag, "with parent:", parent1Tags, "and gps:", grandParent1Tags)
		print("with", tag_, "with parent:", parent2Tags, "and gps:", grandParent2Tags, ":", refMaps.tagEqlMap[tag.lower()][1] == context.Context(parent1Tags, grandParent1Tags), "\n")


	if levelUp(tag, parent2Tags):
		print("leveling up:", tag_, "to", parent2Tags, "because of:", tag)
		for ptag in parent2Tags:
			equalContextTags(tag, ptag, parent1Tags, grandParent2Tags, grandParent1Tags, None)
	elif levelUp(tag_, parent1Tags):
		equalContextTags(parent1Tags, tag_, grandParent1Tags, parent2Tags, None, grandParent2Tags)


	elif (tag.lower() in refMaps.tagEqlMap and tag_.lower() in refMaps.tagEqlMap[tag.lower()][0]
		and refMaps.tagEqlMap[tag.lower()][1] == context.Context(parent1Tags, grandParent1Tags)):
			return True

	elif (tag_.lower() in refMaps.tagEqlMap and tag.lower() in refMaps.tagEqlMap[tag_.lower()][0]
		and refMaps.tagEqlMap[tag_.lower()][1] == context.Context(parent2Tags, grandParent2Tags)):
			return True

	'''
	if (tag.lower() in tagEqlMap2 and tagEqlMap2[tag.lower()][0] == tag_.lower() 
		and tagEqlMap2[tag.lower()][1] == Context(parent1Tags, grandParent1Tags)):
			return True

	elif (tag_.lower() in tagEqlMap2 and tagEqlMap2[tag_.lower()][0] == tag.lower()
		and tagEqlMap2[tag_.lower()][1] == Context(parent2Tags, grandParent2Tags)):
			return True
	'''

	return False


def levelUp(tag, parent2):
	if tag == "binary": print("checking level up of", tag, "and", parent2)

	if parent2 == None: return False
	if tag.lower() in refMaps.tagEqlMap and "*" in refMaps.tagEqlMap[tag.lower()][0]: print("checking level up of", tag, "and", parent2)
	for ptag in parent2:
		if(tag.lower() in refMaps.tagEqlMap and "*" in refMaps.tagEqlMap[tag.lower()][0] and ptag in refMaps.tagEqlMap[tag.lower()][0]): return True

	return False



