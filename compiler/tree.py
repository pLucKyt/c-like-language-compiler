class ASTNode:
    def __init__(self, node_type, children = None, value = None, row = None, col = None): # children = None
        self.type = node_type
        self.children = children if children is not None else []
        self.value = value
        self.row = row
        self.col = col

    def __repr__(self, level = 0):
        ret = "  " * level + f"{self.type}: {self.value if self.value else ''}\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret

"""
ASTNode Types:
Program
Datatype
Identifier
FunctionDeclaration
Parameter
ParameterList
FunctionCall
ArgumentList
VariableDeclaration
Assignment
AssignTypeOperator
IfStatement
ElifStatement
ElseStatement
Empty
ForStatement
WhileStatement
ReturnStatement
ExpressionStatement
Block
Operator
LogicalOr
LogicalAnd
Equality
Comparison
Term
Factor
Unary
Literal
Grouping
"""