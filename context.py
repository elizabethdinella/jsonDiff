import utils

class Context:
	def __init__(self, parentTags=None, grandParentTags=None):
		self.parentTags = parentTags
		self.grandParentTags = grandParentTags

	def __eq__(self, other):
		if self.parentTags == ["*"] or other.parentTags == ["*"]: return True

		if (not self.parentTags == None and not other.parentTags == None):
			print("checking if tags", self.parentTags, "and", other.parentTags, "match: ", utils.tagsMatch(self.parentTags, other.parentTags, self.grandParentTags, other.grandParentTags))


		if (not self.parentTags == None and not other.parentTags == None and 
			not utils.tagsMatch(self.parentTags, other.parentTags, self.grandParentTags, other.grandParentTags)):
				return False


		if (not self.grandParentTags == None and not other.grandParentTags == None):
			print("checking if gp tags", self.grandParentTags, "and", other.grandParentTags, "match: ", utils.tagsMatch(self.grandParentTags, other.grandParentTags, None, None))


	
		if (not self.grandParentTags == None and not other.grandParentTags == None and 
			not utils.tagsMatch(self.grandParentTags, other.grandParentTags, None, None)):
				return False

		if self.parentTags == None and not other.parentTags == None: return False
		if not self.parentTags == None and other.parentTags == None: return False
		if self.grandParentTags == None and not other.grandParentTags == None: return False
		if not self.grandParentTags == None and other.grandParentTags == None: return False

		return True



