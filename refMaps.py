import context
import eqTag

#create an equalTag object -> has a context and a list of tags

#commonAST construct -> other language construct

emptyCntxt = context.Context()
classNoCntxt = eqTag.EqTag(["class"], emptyCntxt, "py")
functionNoCntxt = eqTag.EqTag(["function"], emptyCntxt, "py")
#bodyNoCntxt = eqTag.EqTag(["body"], emptyCntxt, "py") 
augAssignNoCntxt = eqTag.EqTag(["augmented", "assign"], emptyCntxt, "py") 
binOpNoCntxt = eqTag.EqTag(["binary", "operator"], emptyCntxt, "py") 
bodyIfCntxt = eqTag.EqTag(["body"], context.Context(["case"],["if"]), "py")
bodyForCntxt = eqTag.EqTag(["body"], context.Context(["for"],["*"]), "py")
bodyWhileCntxt = eqTag.EqTag(["body"], context.Context(["while"], ["*"]), "py")
elseIfCntxt = eqTag.EqTag(["else"], context.Context(["if"],["*"]), "py")
eqBinOpCntxt = eqTag.EqTag(["equals"], context.Context(["binary", "operator"], ["*"]), "py")

tagEqlMap = dict({"classdef": [classNoCntxt], #classdef matches to class in any context
			"functiondef": [functionNoCntxt], 
			"compoundstmt": [bodyIfCntxt, bodyForCntxt, bodyWhileCntxt, elseIfCntxt],
			"augassign": [augAssignNoCntxt],
			"binop": [binOpNoCntxt],
			"comparison": [eqBinOpCntxt]})


