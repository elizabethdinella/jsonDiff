import context

tagEqlMap = dict({"classdef": (["class"], context.Context()), #classdef matches to class in any context
			"functiondef": (["function"], context.Context()), 
			"compoundstmt": (["body"], context.Context()),
			"augassign": (["augmented", "assign"], context.Context()),
			"binop": (["binary", "operator"], context.Context()),
			"body":(["compoundstmt"], context.Context(["case"],["if"])), 
			"else":(["compoundstmt"], context.Context(["if"], ["*"])), 
			"binary":(["*", "comparison"], context.Context(["case"], ["if"])),
			"binary":(["comparison"], context.Context(["while"],["*"]))})


