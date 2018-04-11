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


def cntxtInsensitiveCheck(eqObj, tags2):
	for tag_ in eqObj.tags:
		if not tag_.lower() in tags2:
			return False
	return True

'''
Checks if two tags are equal using the equality map
'''
def equalTags(tags1, tags2, parent1, parent2):
	
	for tag in tags1: #loop through each tag
		if tag == "*": return True

		#if it is a key in the equality map with an empty context
		if tag.lower() in refMaps.tagEqlMap:
			for eqObj in refMaps.tagEqlMap[tag.lower()]:
				if eqObj.context == context.Context() and cntxtInsensitiveCheck(eqObj, tags2): return True
				elif cntxtInsensitiveCheck(eqObj, tags2) and equalContextTagsWrapper(eqObj, parent1):  
					print("context sensitive match!")
					return True
				
	return False

def equalContextTagsWrapper(eqObj, parent1):

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



