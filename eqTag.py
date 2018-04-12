import utils
import context

class EqTag:
	def __init__(self, _listOfTags, _context, language):
		self.tags = _listOfTags
		self.context = _context
		self.lang = language
		#self.lookahead = lookahead
		#self.confidence = confidence


	'''
	def calculateConfidence(lookahead):
		if self.lang == "py" and "else" in self.tags and lookahead == None:
			self.confidence = 0
		else:
			self.confidence = 1

	'''

