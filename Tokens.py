from enum import Enum
class Token_type(Enum):  # listing all tokens type
    Read = 0
    Setq = 1
    Write = 2
    Defvar = 3
    Dotimes = 4
    When = 5
    EqualOp = 6
    LessThanOp = 7
    GreaterThanOp = 8
    NotEqualOp = 9
    PlusOp = 10
    MinusOp = 11
    MultiplyOp = 12
    DivideOp = 13
    LessThanOrEqualOp = 14
    GreaterThanOrEqualOp = 15
    String = 16
    Identifier = 17
    Constant = 18
    Error = 19
    ModOp = 20
    RemainderOp = 21
    IncrementOp = 22
    DecrementOp = 23
    TrueValue = 24
    FalseValue = 25
    LeftBracket = 26
    RightBracket = 27
    Comment = 28


# class token to hold string and token type
class token:
    def __init__(self, lex, token_type):
        self.lex = lex
        self.token_type = token_type

    def to_dict(self):
        return {
            'Lex': self.lex,
            'token_type': self.token_type
        }


# Reserved word Dictionary
ReservedWords = {"read": Token_type.Read,
                 "setq": Token_type.Setq,
                 "defvar": Token_type.Defvar,
                 "dotimes": Token_type.Dotimes,
                 "when": Token_type.When,
                 "write": Token_type.Write,
                 "t": Token_type.TrueValue,
                 "nil": Token_type.FalseValue

                 }
Operators = {
    "=": Token_type.EqualOp,
    "+": Token_type.PlusOp,
    "-": Token_type.MinusOp,
    "*": Token_type.MultiplyOp,
    "/": Token_type.DivideOp,
    "<": Token_type.LessThanOp,
    ">": Token_type.GreaterThanOp,
    "<=": Token_type.LessThanOrEqualOp,
    ">=": Token_type.GreaterThanOrEqualOp,
    "<>": Token_type.NotEqualOp,
    "mod": Token_type.ModOp,
    "rem": Token_type.RemainderOp,
    "incf": Token_type.IncrementOp,
    "decf": Token_type.DecrementOp

}