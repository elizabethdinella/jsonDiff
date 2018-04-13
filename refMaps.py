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
bodyIfCntxt = eqTag.EqTag(["body"], context.Context(["\*"],["\*"],["case"],["if"]), "py")
bodyForCntxt = eqTag.EqTag(["body"], context.Context(["\*"],["\*"],["for"],["\*"]), "py")
bodyWhileCntxt = eqTag.EqTag(["body"], context.Context(["\*"],["\*"],["while"], ["\*"]), "py")
bodyFuncCntxt = eqTag.EqTag(["body"], context.Context(["\*"],["\*"],["function"],["\*"]), "py")
elseIfCntxt = eqTag.EqTag(["else"], context.Context(["\*"],["\*"],["if"],["\*"]), "py")
lteBinOpCntxt = eqTag.EqTag(["binary", "operator"], context.Context(["lte"],["\*"], ["\*"],["\*"]), "py")
ltBinOpCntxt = eqTag.EqTag(["binary", "operator"], context.Context(["lessthan"],["\*"], ["\*"],["\*"]), "py")
gtBinOpCntxt = eqTag.EqTag(["binary", "operator"], context.Context(["gt"],["\*"], ["\*"],["\*"]), "py")
gteBinOpCntxt = eqTag.EqTag(["binary", "operator"], context.Context(["gte"],["\*"], ["\*"],["\*"]), "py")
eqBinOpCntxt = eqTag.EqTag(["binary", "operator"], context.Context(["equals"],["\*"], ["\*"],["\*"]), "py")
caseIfCntxt = eqTag.EqTag(["case"], context.Context(["\*"], ["\*"], ["if"],["\*"]), "py")


tagEqlMap = dict({"classdef": [classNoCntxt], #classdef matches to class in any context
			"functiondef": [functionNoCntxt], 
			"compoundstmt": [bodyIfCntxt, bodyForCntxt, bodyWhileCntxt, bodyFuncCntxt, elseIfCntxt],
			"augassign": [augAssignNoCntxt],
			"binop": [binOpNoCntxt],
			"comparison": [eqBinOpCntxt, gtBinOpCntxt, gteBinOpCntxt, ltBinOpCntxt, lteBinOpCntxt],
			"if": [caseIfCntxt]})


assignContext =  context.Context(["\*"],["\*"],["assign"],["\*"])
functionContext =  context.Context(["\*"],["\*"],["function"],["\*"])
paramContext =  context.Context(["\*"],["\*"],["parameters"],["\*"])
accessContext =  context.Context(["\*"],["\*"],["access"],["\*"])
binOpContext = context.Context(["\*"], ["\*"],["binary", "operator"], ["\*"])
adlDetailMap = dict({"literal": [assignContext, binOpContext],
			"string": [assignContext, binOpContext],
			"gt": [binOpContext],
			"gte": [binOpContext],
			"lessthan": [binOpContext],
			"lte": [binOpContext],
			"eq": [binOpContext],
			"and": [binOpContext],
			"or": [binOpContext],
			"variable": [assignContext, accessContext, binOpContext],
			"parameters": [functionContext],
			"parameter": [paramContext],
			"access": [assignContext, binOpContext],
			"minus": [binOpContext],
			"plus": [binOpContext],
			"exponent": [binOpContext],
			"multiply":[binOpContext]})

classContext = context.Context(["\*"],["\*"],["class"],["\*"])
ifContext = context.Context(["\*"],["!case"],["if"],["\*"]) #! signifys not

ifElseContext = context.Context(["+case"], ["\*"], ["\*"], ["\*"])
callContext = context.Context(["\*"],["\*"],["call"],["\*"])
functionContext = context.Context(["\*"],["\*"],["functiondef"],["\*"])
noChildrenContext = context.Context(None,["\*"], ["if"], ["\*"])
whileNoChildrenContext = context.Context(None,["\*"], ["while"], ["\*"])
forNoChildrenContext = context.Context(None,["\*"], ["for"], ["\*"])
adlStructMap = dict({"body":[classContext], 
			"case":[ifContext], 
			"args":[callContext], 
			"if": [ifElseContext],
			"else": [noChildrenContext, whileNoChildrenContext, forNoChildrenContext],
			"argument":[callContext],
			"paren":[emptyCntxt],
			"identifier":[functionContext]})

