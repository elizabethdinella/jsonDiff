import utils

class Context:
	def __init__(self, parentTags=None, grandParentTags=None):
		self.parentTags = parentTags
		self.grandParentTags = grandParentTags
		self.dummyParent = dict({"tags": parentTags})
		self.dummyGP = dict({"tags": grandParentTags})

	def __eq__(self, other):
		if self.parentTags == ["*"] or other.parentTags == ["*"]: return True

		if (not self.parentTags == None and not other.parentTags == None and 
			not utils.tagsMatch(self.dummyParent, other.dummyParent, self.dummyGP, other.dummyGP)):
				return False
	
		if (not self.grandParentTags == None and not other.grandParentTags == None and 
			not utils.tagsMatch(self.dummyGP, other.dummyGP, None, None)):
				return False

		if self.parentTags == None and not other.parentTags == None: return False
		if not self.parentTags == None and other.parentTags == None: return False
		if self.grandParentTags == None and not other.grandParentTags == None: return False
		if not self.grandParentTags == None and other.grandParentTags == None: return False

		return True

	def __str__(self): 
		return "parent tags " + self.parentTags[0] + " gp tags " + self.grandParentTags[0]