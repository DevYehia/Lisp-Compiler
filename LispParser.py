from Tokens import *
from nltk.tree import *


class Parser:
    #The attributes of this class are:
    #errors: A list of syntax errors by parsing if exist
    #tokens_List: A list with all the tokens from the scanner
    #delimiter_List: A list of all delimeters indices in the tokens_List array if exists
    def __init__(self,Globalerrors,Globaltokens_list,Globaldelimiter_List):
        self.errors = Globalerrors
        self.tokens_List = Globaltokens_list
        self.delimiter_List = Globaldelimiter_List
        print(self.tokens_List)

    #The start of the parsing sequence
    #This function calls the function line for every line of code
    #until all tokens are processed
    def Parse(self):
        j = 0
        Children = []
        out = self.Line(j)
        Children.append(out["node"])
        while (out["index"] < len(self.tokens_List)):
            print(out["index"])
            out = self.Line(out["index"])
            Children.append(out["node"])
        print (Children)
        return Tree("Program", Children)

    # A Line in Lisp is composed of
    # Line ----> ( Statement )
    def Line(self, j):
        Children = []
        out = dict()

        # Check For Left Parentheses
        out = self.Match(Token_type.LeftBracket, j, "Left Bracket")
        if out["node"] == "error":
            self.errors.append("Syntax error : " + self.tokens_List[j]['Lex'] + " Expected Left Bracket")
            out["index"] = self.getNextDelimiter(j) + 1
            Children.append("error")
            return out

        Children.append(out["node"])

        # Check for Statement
        if out["index"] < len(self.tokens_List):
            out = self.Statment(out["index"], Children)
        else:
            Children.append("error")
            self.errors.append("Syntax error : Expected Statement")
            Children.append("error")
            self.errors.append("Syntax error : Expected Right Bracket")
            t = Tree("Line", Children)
            return {"node": t, "index": out["index"]}

        if out["index"] < len(self.tokens_List):
            if self.tokens_List[out["index"]]["token_type"] == Token_type.RightBracket:
                out = self.Match(self.tokens_List[out["index"]]["token_type"], out["index"])
                Children.append(out["node"])
            else:
                out["node"] = "error"
                Children.append(out["node"])
                errorLex = self.tokens_List[out["index"]]["Lex"]
                out["index"] = self.getNextDelimiter(out["index"])
                if out["index"] < len(self.tokens_List):
                    out["index"] = out["index"] + 1
                self.errors.append("Syntax error : " + errorLex + " Expected Right Bracket")

        else:
            Children.append("error")
            self.errors.append("Syntax error : Non-Closed Left Bracket")
            t = Tree("Line", Children)
            return {"node": t, "index": out["index"]}

        t = Tree("Line", Children)
        return {"node": t, "index": out["index"]}

    


    def Statment(self, j, Children):
        out = dict()
        ch = []
        if self.tokens_List[j]["token_type"] == Token_type.Read:
            out = self.Match(self.tokens_List[j]["token_type"], j)
            Children.append(out["node"])
            if out["index"] < len(self.tokens_List):
                if self.tokens_List[out["index"]]["token_type"] == Token_type.Identifier:
                    out = self.Match(Token_type.Identifier, out["index"])
                    Children.append(Tree("Identifier" ,[out["node"]]))
                else:
                    out["node"] = "error"
                    self.errors.append(
                        "Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Identifier")
                    out["index"] = self.getNextDelimiter(out["index"])

                    Children.append(Tree("Identifier" ,[out["node"]]))
                    return out
            else:
                Children.append(Tree("Identifier" ,["error"]))
                self.errors.append("End of Token Stream: Expected Identifier")
                return {"node": Tree("Statement", Children), "index": out["index"]}

        elif self.tokens_List[j]["token_type"] == Token_type.Setq:
            out = self.Match(self.tokens_List[j]["token_type"], j)
            ch.append(out["node"])
            if out["index"] < len(self.tokens_List):
                if self.tokens_List[out["index"]]["token_type"] == Token_type.Identifier:
                    out = self.Match(Token_type.Identifier, out["index"])
                    ch.append(Tree("Identifier",[out["node"]]))
                else:
                    out["node"] = "error"
                    self.errors.append("Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Identifier")
                    out["index"] = self.getNextDelimiter(out["index"])
                    ch.append("error")
                    Children.append(Tree("Statement",[Tree("Assignment",ch)]))
                    return {"node": None, "index": out["index"]}
            else:
                ch.append("error")
                self.errors.append("End of Token Stream: Expected Identifier")
                Children.append(Tree("Statement",[Tree("Assignment",ch)]))
                return {"node": None, "index": out["index"]}

            out = self.Assignment(out["index"], ch)
            Children.append(Tree("Statement",[Tree("Assignment",ch)]))
            return {"node": None, "index": out["index"]}

        elif self.tokens_List[j]["token_type"] == Token_type.When:
            out = self.when(j, ch)
            Children.append(Tree("Statement",[Tree("WhenStatement",ch)]))
            return {"node": None, "index": out["index"]}


        elif self.tokens_List[j]["token_type"] == Token_type.Dotimes:
            out = self.doTimes(j, ch)
            Children.append(Tree("Statement",[Tree("DoTimesStatement",ch)]))
            return {"node": None, "index": out["index"]}

        # Check for function
        elif self.tokens_List[j]["token_type"] == Token_type.Identifier:
            out = self.Match(Token_type.Identifier, j)
            ch.append(Tree("Identifier",[out["node"]]))
            out = self.Parameters(out["index"], ch)
            t = Tree("Function", ch)
            Children.append(Tree("Statement",[t]))
            return {"node": t, "index": out["index"]}

        elif self.tokens_List[j]["token_type"] == Token_type.Write:
            out = self.write(j, ch)
            Children.append(Tree("Statement",[Tree("WriteStatement",ch)]))
            return {"node": None, "index": out["index"]}

        elif self.tokens_List[j]["token_type"] == Token_type.Defvar:
            out = self.Defvarstatement(j, ch)
            Children.append(Tree("Statement",[Tree("DefVarStatement",ch)]))
            return {"node": t, "index": out["index"]}

        else:
            out = self.expression(j, Children)

        t = Tree("Statement", Children)
        return {"node": t, "index": out["index"]}


    def Defvarstatement(self,j, Children):
        out = dict()
        out = self.Match(self.tokens_List[j]["token_type"], j)
        Children.append(out["node"])
        if out["index"] < len(self.tokens_List):
            if self.tokens_List[out["index"]]["token_type"] == Token_type.Identifier:
                out = self.Match(self.tokens_List[out["index"]]["token_type"], out["index"])
            else:
                out["node"] = "error"
                self.errors.append("Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Identifier")
            Children.append(Tree("Identifier" , [out["node"]]))
        else:
            Children.append("error")
            Children.append(Tree("Identifier" , [out["node"]]))
            self.errors.append("End of Token Stream : Expected Identifier")
            return {"node": Children, "index": out["index"]}
        Children2 = []
        out = self.Defvalue(out["index"], Children2)
        Children.append(Tree("DefValue",Children2))
        return {"node": Children, "index": out["index"]}


    def Defvalue(self,j,Children):
        out = dict()
        index = j
        if j < len(self.tokens_List):
            Op = self.NoExpParam(j)
            if Op["node"] != None:
                if Op["node"] == Token_type.Identifier:
                    Children.append(Tree("NoExpParam",[Tree("Identifier",[self.tokens_List[j]["Lex"]])]))
                elif Op["node"] == Token_type.Constant:
                    Children.append(Tree("NoExpParam",[Tree("Constant",[self.tokens_List[j]["Lex"]])]))                
                else:
                    Children.append(Tree("NoExpParam",[Tree("String",[self.tokens_List[j]["Lex"]])]))          
                return {"node": None, "index": j+1}
            
            if self.tokens_List[j]["token_type"] == Token_type.LeftBracket:
                Children.append("(")
                index = self.DefValueOption(j+1,Children)

            

            return {"node": None, "index": index}

        else:
            return {"node": None, "index": j}

    def DefValueOption(self,j,Children):
        if j < len(self.tokens_List):
            if self.tokens_List[j]["token_type"] == Token_type.Read:
                Children.append("read")
                j+=1
            else:
                out = self.expression(j,Children)
                j = out["index"]
            if j < len(self.tokens_List):
                if self.tokens_List[j]["token_type"] == Token_type.RightBracket:
                    Children.append(")")
                    j+=1
                else:
                    Children.append("error")
                    self.errors.append("Syntax Error " + self.tokens_List[j]["Lex"] + " Expected Right Bracket")
                    j = self.getNextDelimiter(j)+1
            else:
                Children.append("error")
                self.errors.append("End of Token Stream Expected Right Bracket")
        else:
            Children.append("error")
            self.errors.append("End of Token Stream Expected DefValue")
        return j





    def write(self,j, children):
        Children = []
        out = self.Match(Token_type.Write, j)
        Children.append(out["node"])
        Op = self.Param(out["index"],Children)

        if Op["node"] != None:
                out["index"] = Op["index"]

        else:
            Children.append("error")
            self.errors.append("Syntax error : Expected Identifier or Constant or String")

        t = Tree("Write", Children)
        children.append(t)
        return {"node": t, "index": out["index"]}


    def Assignment(self,j, Children):
    
        if j < len(self.tokens_List):
            out = self.AssignmentValue(j, Children)
        else:
            Children.append("error")
            self.errors.append("End of Token Stream : Expected Assignment Value")
            t = Tree("Assignment", Children)
            return {"node": t, "index": j}
        print("index is " ,out["index"])
        return {"node": Children, "index": out["index"]}


    def AssignmentValue(self, j, OutChildren):
        Children = []
        out = dict()
        out["index"] = j
        Op = self.NoExpParam(j)
        if Op["node"] != None:
            if Op["node"] == Token_type.Identifier:
                Children.append(Tree("NoExpParam",[Tree("Identifier",[self.tokens_List[j]["Lex"]])]))
            elif Op["node"] == Token_type.Constant:
                Children.append(Tree("NoExpParam",[Tree("Constant",[self.tokens_List[j]["Lex"]])]))                
            else:
                Children.append(Tree("NoExpParam",[Tree("String",[self.tokens_List[j]["Lex"]])]))                        
            OutChildren.append(Tree("AssignmentValue",Children))
            out["index"] += 1
        else:
            if self.tokens_List[j]["token_type"] == Token_type.LeftBracket:
                out = self.Match(Token_type.LeftBracket, j)
            else:
                out["node"] = "error"
                out["index"] = self.getNextDelimiter(j)
                self.errors.append("Syntax error : " + self.tokens_List[j]['Lex'] + " Expected Assignement Value")
                Children.append("error")
                OutChildren.append(Tree("AssignmentValue",Children))
                return out
            Children.append(out["node"])

            if out["index"] < len(self.tokens_List):
                out = self.Ass(out["index"], Children)
            else:
                Children.append("error")
                self.errors.append("Syntax error : Expected Ass")
                Children.append("error")
                self.errors.append("Syntax error : Expected Right Bracket")
                OutChildren.append(Tree("AssignmentValue",Children))
                t = Tree("Assignment", Children)
                return {"node": t, "index": out["index"]}

            if out["index"] < len(self.tokens_List):
                if self.tokens_List[out["index"]]["token_type"] == Token_type.RightBracket:
                    out = self.Match(Token_type.RightBracket, out["index"])
                else:
                    out["node"] = "error"
                    out["index"] = self.getNextDelimiter(out["index"])
                    self.errors.append(
                        "Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Right Bracket")
                Children.append(out["node"])
            else:
                Children.append("error")
                self.errors.append("Syntax error : Non-Closed Left Bracket")
                OutChildren.append(Tree("AssignmentValue",Children))
                t = Tree("Line", Children)
                return {"node": t, "index": out["index"]}
            OutChildren.append(Tree("AssignmentValue",Children))

        return {"node": "error", "index": out["index"]}

    def Param(self,j,OutChildren):
        Children = []
        if self.tokens_List[j]["token_type"] == Token_type.Identifier:
            paramType = Token_type.Identifier
            Children.append(Tree("Identifier",[self.tokens_List[j]["Lex"]]))
            OutChildren.append(Tree("Param",Children))
        elif self.tokens_List[j]["token_type"] == Token_type.Constant:
            paramType = Token_type.Constant
            Children.append(Tree("Constant",[self.tokens_List[j]["Lex"]]))
            OutChildren.append(Tree("Param",Children))
        elif self.tokens_List[j]["token_type"] == Token_type.String:
            paramType = Token_type.String
            Children.append(Tree("String",[self.tokens_List[j]["Lex"]]))
            OutChildren.append(Tree("Param",Children))
        elif self.tokens_List[j]["token_type"] == Token_type.LeftBracket:
            out = self.BracketedExpression(j,Children)
            OutChildren.append(Tree("Param",Children))            
            return {"node": "(", "index": out["index"]}
        else:
            paramType = None
        return {"node": paramType, "index": j+1}

    def NoExpParam(self,j):
        if self.tokens_List[j]["token_type"] == Token_type.Identifier:
            paramType = Token_type.Identifier
        elif self.tokens_List[j]["token_type"] == Token_type.Constant:
            paramType = Token_type.Constant
        elif self.tokens_List[j]["token_type"] == Token_type.String:
            paramType = Token_type.String
        else:
            paramType = None
        return {"node": paramType, "index": j+1}
    
    def Ass(self,j,Children):
        out = dict()

        if self.tokens_List[j]["token_type"] == Token_type.Read:
            out = self.Match(Token_type.Read, j)
            Children.append(out["node"])
            return {"node": Children, "index": out["index"]}
        else:
            out = self.expression(j,Children)

            #t = Tree("Expression", Children)
            return {"node": Children, "index": out["index"]}


    def ArithOp(self,j):
        if(self.tokens_List[j]["token_type"] == Token_type.PlusOp):
            OpType = self.tokens_List[j]["token_type"]
        elif(self.tokens_List[j]["token_type"] == Token_type.MinusOp):
            OpType = self.tokens_List[j]["token_type"]
        elif(self.tokens_List[j]["token_type"] == Token_type.MultiplyOp):
            OpType = self.tokens_List[j]["token_type"]
        elif(self.tokens_List[j]["token_type"] == Token_type.DivideOp):
            OpType = self.tokens_List[j]["token_type"]
        else:
            OpType = None
        return {"node":OpType,"index":j+1}


    def RelOp(self,j):
        if(self.tokens_List[j]["token_type"] == Token_type.EqualOp):
            OpType = self.tokens_List[j]["token_type"]
        elif(self.tokens_List[j]["token_type"] == Token_type.NotEqualOp):
            OpType = self.tokens_List[j]["token_type"]
        elif(self.tokens_List[j]["token_type"] == Token_type.GreaterThanOp):
            OpType = self.tokens_List[j]["token_type"]
        elif(self.tokens_List[j]["token_type"] == Token_type.GreaterThanOrEqualOp):
            OpType = self.tokens_List[j]["token_type"]
        elif(self.tokens_List[j]["token_type"] == Token_type.LessThanOp):
            OpType = self.tokens_List[j]["token_type"]
        elif(self.tokens_List[j]["token_type"] == Token_type.LessThanOrEqualOp):
            OpType = self.tokens_List[j]["token_type"]
        else:
            OpType = None
        return {"node":OpType,"index":j+1}


    def IncOp(self,j):
        if(self.tokens_List[j]["token_type"] == Token_type.IncrementOp):
            OpType = self.tokens_List[j]["token_type"]
        elif(self.tokens_List[j]["token_type"] == Token_type.DecrementOp):
            OpType = self.tokens_List[j]["token_type"]
        else:
            OpType = None
        return {"node":OpType,"index":j+1}


    def RemOp(self,j):
        if(self.tokens_List[j]["token_type"] == Token_type.RemainderOp):
            OpType = self.tokens_List[j]["token_type"]
        elif(self.tokens_List[j]["token_type"] == Token_type.ModOp):
            OpType = self.tokens_List[j]["token_type"]
        else:
            OpType = None
        return {"node":OpType,"index":j+1}


    def expression(self,j,children):
        Children = []
        out = dict()
        print("Index is ",j)
        Op = self.ArithOp(j)
        if Op["node"] != None:
            # out = arithmaticOperator(j)
            out = self.Match(self.tokens_List[j]["token_type"], j)
            Children.append(Tree("ArithOp",[out["node"]]))

            if out["index"] < len(self.tokens_List):
                out1 = self.element(out["index"],Children)
                if out1["node"] == "error":
                    nextDel = self.getNextDelimiter(out["index"])
                    t= Tree("Expression", Children)
                    children.append(t)
                    return {"node": t, "index": nextDel}
                if out1["index"] < len(self.tokens_List):
                    print("out ind is " , out1["index"])
                    out = self.elements(out1["index"], Children)
                    
            else:
                Children.append("error")
                self.errors.append("End of token stream : Expected Element")

            t= Tree("Expression", Children)
            children.append(t)
            return {"node": None, "index": out["index"]}

        Op = self.RelOp(j)
        if Op["node"] != None:
            out = self.Match(self.tokens_List[j]["token_type"], j)
            Children.append(Tree("RelOp",[out["node"]]))

            if out["index"] < len(self.tokens_List):
                out1 = self.element(out["index"],Children)
                if(out1["node"] == "error"):
                    nextDel = self.getNextDelimiter(out["index"])
                    t= Tree("Expression", Children)
                    children.append(t)
                    return {"node": t, "index": nextDel}
                out = out1
            else:
                Children.append("error")
                self.errors.append("End of Token Stream : Expected Element")
            if out["index"] < len(self.tokens_List):
                out1 = self.element(out["index"],Children)
                if(out1["node"] == "error"):
                    nextDel = self.getNextDelimiter(out["index"])
                    t= Tree("Expression", Children)
                    children.append(t)
                    return {"node": t, "index": nextDel}
                out = out1
            else:
                Children.append("error")
                self.errors.append("End of Token Stream : Expected Element")

            t = Tree("Expression",Children)
            children.append(t)
            return {"node": t, "index": out["index"]}

        Op = self.RemOp(j)
        if Op["node"] != None:
            out = self.Match(self.tokens_List[j]["token_type"], j)
            Children.append(Tree("RemOp",[out["node"]]))

            if out["index"] < len(self.tokens_List):
                out1 = self.element(out["index"],Children)
                if(out1["node"] == "error"):
                    nextDel = self.getNextDelimiter(out["index"])
                    t= Tree("Expression", Children)
                    children.append(t)
                    return {"node": t, "index": nextDel}
                out = out1
            else:
                Children.append("error")
                self.errors.append("End of Token Stream : Expected Element")
            if out["index"] < len(self.tokens_List):
                out1 = self.element(out["index"],Children)
                if(out1["node"] == "error"):
                    nextDel = self.getNextDelimiter(out["index"])
                    t= Tree("Expression", Children)
                    children.append(t)
                    return {"node": t, "index": nextDel}
                out = out1
            else:
                Children.append("error")
                self.errors.append("End of Token Stream : Expected Element")

            t = Tree("Expression",Children)
            children.append(t)
            return {"node": t, "index": out["index"]}

        Op = self.IncOp(j)

        if Op["node"] != None:
            out = self.Match(self.tokens_List[j]["token_type"], j)
            Children.append(Tree("IncOp",[out["node"]]))

            if out["index"] < len(self.tokens_List):
                out1 = self.element(out["index"],Children)
                if(out1["node"] == "error"):
                    nextDel = self.getNextDelimiter(out["index"])
                    t= Tree("Expression", Children)
                    children.append(t)
                    return {"node": t, "index": nextDel}
                out = out1


            else:
                Children.append("error")
                self.errors.append("End of Token Stream : Expected Element")
            if out["index"] < len(self.tokens_List):
                out = self.nullableElement(out["index"],Children)


            t = Tree("Expression", Children)
            children.append(t)            
            return {"node": t, "index": out["index"]}
        return {"node": "error", "index": j+1}
    
    def BracketedExpression(self,j,Children):
        out = dict()
        out = self.Match(Token_type.LeftBracket,j)
        Children.append(out["node"])
        out = self.expression(out["index"],Children)
        if out["index"] < len(self.tokens_List):
            out = self.Match(Token_type.RightBracket,out["index"])
            Children.append(out["node"])
        else:
            self.errors.append("End of Token Stream Expected Right bracket")
            Children.append("error")
        return {"node":None,"index":out["index"]}

    def element(self,j,OutChildren):
        Children = []
        out = dict()
        if self.tokens_List[j]["token_type"] == Token_type.Identifier or self.tokens_List[j]["token_type"] == Token_type.Constant:
            out = self.Match(self.tokens_List[j]["token_type"], j)
        elif self.tokens_List[j]["token_type"] == Token_type.LeftBracket:
            out = self.BracketedExpression(j,Children)
        else:
            out["node"] = "error"
            out["index"] = j
            self.errors.append("Syntax error :"+ self.tokens_List[j]["Lex"]+ " Expected Identifier or Constant")
        if out["node"] != None:
            Children.append(out["node"])
        OutChildren.append(Tree("Element",Children))
        return {"node": None, "index": out["index"]}

    def nullableElement(self,j,Children):
        out = dict()
        if self.tokens_List[j]["token_type"] == Token_type.Identifier or self.tokens_List[j]["token_type"] == Token_type.Constant:
            out = self.Match(self.tokens_List[j]["token_type"], j)
        elif self.tokens_List[j]["token_type"] == Token_type.LeftBracket:
            out = self.BracketedExpression(j,Children)
        else:
            out["node"] = "error"
            out["index"] = j
        if out["node"] != "error":
            Children.append(Tree("Element",[out["node"]]))
        return out

    def elements(self,j,OutChildren):
        Children = []
        out = dict()
        if j < len(self.tokens_List):
            if self.tokens_List[j]["token_type"] == Token_type.Identifier or self.tokens_List[j]["token_type"] == Token_type.Constant or self.tokens_List[j]["token_type"] == Token_type.LeftBracket:
                out = self.element(j,Children)
                out = self.elements(out["index"], Children)
                OutChildren.append(Tree("Elements",Children))            
                return {"node": "SMth", "index": out["index"]}
            elif self.tokens_List[j]["token_type"] == Token_type.RightBracket:

                return {"node": None, "index": j}
            else:
                self.errors.append("Syntax error "+self.tokens_List[j]["Lex"]+" Expected Element")
                Children.append("error")
                OutChildren.append(Tree("Element",Children))
                return {"node": "error", "index": self.getNextDelimiter(j)}
        else:
            return {"node": None, "index": j}

    def Parameters(self,j,OutChildren):
        Children = []
        out = dict()
        if j < len(self.tokens_List):
            Op = self.Param(j,Children)
            if Op["node"] != None:
                if Op["node"] != "(":
                    out = self.Match(self.tokens_List[j]["token_type"], j)
                    out = self.Parameters(out["index"], Children)
                else:
                    out = self.Parameters(Op["index"],Children)
                OutChildren.append(Tree("Params",Children))
                return {"node": None, "index": out["index"]}
            else:
                return {"node": None, "index": j}
        else:
            return {"node": None, "index": j}


    def incValue(self,j):
        Children = []
        out = dict()
        if self.tokens_List[j]["token_type"] == Token_type.Identifier or self.tokens_List[j]["token_type"] == Token_type.Constant:
            out = self.element(j,Children)
            Children.append(out["node"])
            t = Tree("incValue", Children)
            return {"node": t, "index": out["index"]}
        else:
            return {"node": Tree(), "index": j}

    def when(self, j, Children):
        out = dict()
        out = self.Match(self.tokens_List[j]["token_type"], j)
        Children.append(out["node"])

        if out["index"] < len(self.tokens_List):
            if self.tokens_List[out["index"]]["token_type"] == Token_type.LeftBracket:
                out = self.Match(self.tokens_List[out["index"]]["token_type"], out["index"])
            else:
                out["node"] = "error"
                self.errors.append("Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Left Bracket")
                out["index"] = self.getNextDelimiter(out["index"])+1
                Children.append("error")
                return out
            Children.append(out["node"])
        else:
            out["node"] = "error"
            self.errors.append("End of Token Stream : Expected Left Bracket")
            Children.append(out["node"])
            return {"node": None, "index": j}

        if out["index"] < len(self.tokens_List):
            out = self.expression(out["index"], Children)
        else:
            out["node"] = "error"
            self.errors.append("End of Token Stream : Expected Expression")
            Children.append(out["node"])
            return {"node": None, "index": out["index"]}

        if out["index"] < len(self.tokens_List):
            if self.tokens_List[out["index"]]["token_type"] == Token_type.RightBracket:
                out = self.Match(self.tokens_List[out["index"]]["token_type"], out["index"])
            else:
                out["node"] = "error"
                self.errors.append(
                    "Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Right Bracket")
                out["index"] = self.getNextDelimiter(out["index"])+1
                Children.append("error")
                return out
            Children.append(out["node"])
        else:
            out["node"] = "error"
            self.errors.append("End of Token Stream : Expected RightBracket")
            Children.append(out["node"])
            return {"node": None, "index": out["index"]}

        if out["index"] < len(self.tokens_List):
            if self.tokens_List[out["index"]]["token_type"] == Token_type.LeftBracket:
                out = self.Match(self.tokens_List[out["index"]]["token_type"], out["index"])
            else:
                out["node"] = "error"
                self.errors.append("Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Left Bracket")
                out["index"] = self.getNextDelimiter(out["index"])+1
                Children.append("error")
                return out
            Children.append(out["node"])
        else:
            out["node"] = "error"
            self.errors.append("End of Token Stream : Expected LeftBracket")
            Children.append(out["node"])
            return {"node": None, "index": out["index"]}

        if out["index"] < len(self.tokens_List):
            out = self.Statment((out["index"]), Children)
        else:
            out["node"] = "error"
            self.errors.append("End of Token Stream : Expected Statment")
            Children.append(out["node"])
            return {"node": None, "index": out["index"]}
        if out["index"] < len(self.tokens_List):
            if self.tokens_List[out["index"]]["token_type"] == Token_type.RightBracket:
                out = self.Match(self.tokens_List[out["index"]]["token_type"], out["index"])
            else:
                out["node"] = "error"
                self.errors.append(
                    "Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Right Bracket")
                out["index"] = self.getNextDelimiter(out["index"])+1
                Children.append("error")
                return out
            Children.append(out["node"])
        else:
            out["node"] = "error"
            self.errors.append("End of Token Stream : Expected RightBracket")
            Children.append(out["node"])
            return {"node": None, "index": out["index"]}

        out = self.s_(out["index"], Children)

        return {"node": None, "index": out["index"]}

    def s_(self, j, OutChildren):
        Children = []
        out = dict()
        if j < len(self.tokens_List):
            if self.tokens_List[j]["token_type"] == Token_type.LeftBracket:
                out = self.Match(self.tokens_List[j]["token_type"], j)
                Children.append(out["node"])

                if out["index"] < len(self.tokens_List):
                    out = self.Statment(out["index"], Children)
                else:
                    out["node"] = "error"
                    self.errors.append("End of Token Stream : Expected Statment")
                    Children.append(Tree("Statement" ,[out["node"]]))
                    return {"node": None, "index": out["index"]}

                if out["index"] < len(self.tokens_List):
                    if self.tokens_List[out["index"]]["token_type"] == Token_type.RightBracket:
                        out = self.Match(self.tokens_List[out["index"]]["token_type"], out["index"])
                        Children.append(out["node"])
                    else:
                        out["node"] = "error"
                        self.errors.append(
                            "Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Right Bracket")
                        #out["index"] = self.getNextDelimiter(out["index"])
                        Children.append("error")
                        return out

                    out = self.s_(out["index"], Children)
                    OutChildren.append(Tree("SDash",Children))
                else:
                    out["node"] = "error"
                    self.errors.append("End of Token Stream : Expected RightBracket")
                    Children.append(out["node"])
                    return {"node": None, "index": out["index"]}

                return {"node": None, "index": out["index"]}
            else:
                return {"node": None, "index": j}
        else:
            return {"node": None, "index": j}

    def doTimes(self, j, Children):
        out = dict()
        out = self.Match(self.tokens_List[j]["token_type"], j)
        Children.append(out["node"])

        if out["index"] < len(self.tokens_List):
            if self.tokens_List[out["index"]]["token_type"] == Token_type.LeftBracket:
                out = self.Match(self.tokens_List[out["index"]]["token_type"], out["index"])
            else:
                out["node"] = "error"
                self.errors.append(
                    "Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Left Bracket")
                out["index"] = self.getNextDelimiter(out["index"])+1
                Children.append("error")
                return out
            Children.append(out["node"])
        else:
            out["node"] = "error"
            self.errors.append("Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Left Bracket")
            Children.append(out["node"])
            return {"node": None, "index": j}

        if out["index"] < len(self.tokens_List):
            if self.tokens_List[out["index"]]["token_type"] == Token_type.Identifier:
                out = self.Match(self.tokens_List[out["index"]]["token_type"], out["index"])
            else:
                out["node"] = "error"
                self.errors.append(
                    "Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Identifier")
                out["index"] = self.getNextDelimiter(out["index"])+1
                Children.append(Tree("Identifier",["error"]))
                return out
            Children.append(Tree("Identifier",[out["node"]]))
        else:
            out["node"] = "error"
            self.errors.append("Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected an Identifier")
            Children.append(Tree("Identifier",["error"]))
            return {"node": None, "index": out["index"]}

        if out["index"] < len(self.tokens_List):
            if self.tokens_List[out["index"]]["token_type"] == Token_type.Constant:
                out = self.Match(self.tokens_List[out["index"]]["token_type"], out["index"])
            else:
                out["node"] = "error"
                self.errors.append(
                    "Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Constant")
                out["index"] = self.getNextDelimiter(out["index"])+1
                Children.append(Tree("Constant",["error"]))
                return out
            Children.append(Tree("Constant",[out["node"]]))
        else:
            out["node"] = "error"
            self.errors.append("Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected an Constant")
            Children.append(Tree("Constant",["error"]))
            return {"node": None, "index": out["index"]}

        if out["index"] < len(self.tokens_List):
            if self.tokens_List[out["index"]]["token_type"] == Token_type.RightBracket:
                out = self.Match(self.tokens_List[out["index"]]["token_type"], out["index"])
            else:
                out["node"] = "error"
                self.errors.append(
                    "Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Right Bracket")
                out["index"] = self.getNextDelimiter(out["index"])+1
                Children.append("error")            
                return out
            Children.append(out["node"])
        else:
            out["node"] = "error"
            self.errors.append("Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Right Bracket")
            Children.append(out["node"])
            return {"node": None, "index": out["index"]}

        if out["index"] < len(self.tokens_List):
            if self.tokens_List[out["index"]]["token_type"] == Token_type.LeftBracket:
                out = self.Match(self.tokens_List[out["index"]]["token_type"], out["index"])
            else:
                out["node"] = "error"
                self.errors.append(
                    "Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Left Bracket")
                out["index"] = self.getNextDelimiter(out["index"])+1
                Children.append("error")
                return out
            Children.append(out["node"])
        else:
            out["node"] = "error"
            self.errors.append("Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Left Bracket")
            Children.append(out["node"])
            return {"node": None, "index": out["index"]}

        if out["index"] < len(self.tokens_List):
            out = self.Statment((out["index"]),Children)
        else:
            out["node"] = "error"
            self.errors.append("Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected a Statement ")
            Children.append(Tree("Statement",[out["node"]]))
            return {"node": None, "index": out["index"]}
        if out["index"] < len(self.tokens_List):
            if self.tokens_List[out["index"]]["token_type"] == Token_type.RightBracket:
                out = self.Match(self.tokens_List[out["index"]]["token_type"], out["index"])
            else:
                out["node"] = "error"
                self.errors.append(
                    "Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Right Bracket")
                out["index"] = self.getNextDelimiter(out["index"])+1
                Children.append("error")               
                return out
            Children.append(out["node"])
        else:
            out["node"] = "error"
            self.errors.append("Syntax error : " + self.tokens_List[out["index"]]['Lex'] + " Expected Right Bracket")
            Children.append(out["node"])            
            return {"node": None, "index": out["index"]}

        out = self.s_(out["index"], Children)
        return {"node": None, "index": out["index"]}

    def Match(self,a, j,expected="Something"):
        output = dict()
        if (j < len(self.tokens_List)):
            Temp = self.tokens_List[j]
            if (Temp['token_type'] == a):
                j += 1
                output["node"] = Temp['Lex']
                output["index"] = j
                return output
            else:
                output["node"] = "error"
                output["index"] = j + 1
                self.errors.append("Syntax error : " + Temp['Lex'] + " Expected " + expected)
                return output
        else:
            output["node"] = "error"
            output["index"] = j + 1
            return output
        
    def getNextDelimiter(self,index):
        for num in self.delimiter_List:
            if num >= index:
                return num
        return len(self.tokens_List)