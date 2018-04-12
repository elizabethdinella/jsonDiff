import context
import eqTag

adlDetailColor = "#B0B0B0"
adlStrColor = "#8b98ca"
notMatchedColor = "#ff0000"

#create an equalTag object -> has a context and a list of tags

#commonAST construct -> other language construct

emptyCntxt = context.Context()
classNoCntxt = eqTag.EqTag(["class"], emptyCntxt, "py")
functionNoCntxt = eqTag.EqTag(["function"], emptyCntxt, "py")
augAssignNoCntxt = eqTag.EqTag(["augmented", "assign"], emptyCntxt, "py") 
binOpNoCntxt = eqTag.EqTag(["binary", "operator"], emptyCntxt, "py") 
bodyIfCntxt = eqTag.EqTag(["body"], context.Context(["*"],["case"],["if"]), "py")
bodyForCntxt = eqTag.EqTag(["body"], context.Context(["*"],["for"],["*"]), "py")
bodyWhileCntxt = eqTag.EqTag(["body"], context.Context(["*"],["while"], ["*"]), "py")
bodyFuncCntxt = eqTag.EqTag(["body"], context.Context(["*"],["function"],["*"]), "py")
elseIfCntxt = eqTag.EqTag(["else"], context.Context(["*"],["if"],["*"]), "py")
eqBinOpCntxt = eqTag.EqTag(["binary", "operator"], context.Context(["equals"],["*"], ["*"]), "py")

tagEqlMap = dict({"classdef": [classNoCntxt], #classdef matches to class in any context
			"functiondef": [functionNoCntxt], 
			"compoundstmt": [bodyIfCntxt, bodyForCntxt, bodyWhileCntxt, bodyFuncCntxt, elseIfCntxt],
			"augassign": [augAssignNoCntxt],
			"binop": [binOpNoCntxt],
			"comparison": [eqBinOpCntxt]})


assignContext =  context.Context(["*"],["assign"],["*"])
adlDetailMap = dict({"literal": assignContext,
		     "variable": assignContext})

