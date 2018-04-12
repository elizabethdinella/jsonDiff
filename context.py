import utils

class Context:
	def __init__(self, lookaheadTags=None, parentTags=None, grandParentTags=None):
		self.lookaheadTags = lookaheadTags
		self.parentTags = parentTags
		self.grandParentTags = grandParentTags
		self.dummyLookahead = dict({"tags": self.lookaheadTags})
		self.dummyParent = dict({"tags": self.parentTags})
		self.dummyGP = dict({"tags": self.grandParentTags})
		self.dummyNode = dict({"tags": "*"})

	def __eq__(self, other):

		if(not self.lookaheadTags == None and not other.lookaheadTags == None and 
			(utils.tagsMatch(self.dummyLookahead, other.dummyLookahead, self.dummyNode, other.dummyNode) == -1)):
				return False

		if (not self.parentTags == None and not other.parentTags == None and 
			(utils.tagsMatch(self.dummyParent, other.dummyParent, self.dummyGP, other.dummyGP) == -1)):
				return False
	
		if (not self.grandParentTags == None and not other.grandParentTags == None and 
			(utils.tagsMatch(self.dummyGP, other.dummyGP, None, None) == -1)):
				return False

		if self.lookaheadTags == ["*"] or other.lookaheadTags == ["*"]: return True
		if self.parentTags == ["*"] or other.parentTags == ["*"]: return True

		if self.lookaheadTags == None and not other.lookaheadTags == None: return False
		if not self.lookaheadTags == None and other.lookaheadTags == None: return False
		if self.parentTags == None and not other.parentTags == None: return False
		if not self.parentTags == None and other.parentTags == None: return False
		if self.grandParentTags == None and not other.grandParentTags == None: return False
		if not self.grandParentTags == None and other.grandParentTags == None: return False

		return True

	def __str__(self): 
		ret = ""
		if not self.lookaheadTags == None and len(self.lookaheadTags) > 0:
			ret += " lookahead tags " + self.lookaheadTags[0]
		if not self.parentTags == None:
			ret += " parent tags " + self.parentTags[0]
		if not self.grandParentTags == None:
			ret += " gp tags " + self.grandParentTags[0]

		if ret == "":
			ret = "empty context"	
		
		return ret
