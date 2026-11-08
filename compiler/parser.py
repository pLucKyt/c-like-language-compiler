from lexer import *
from tree import *
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'row', 'col'])

function_end_row = None

class ParserError(Exception):
    def __init__(self, message, token):
        super().__init__(f"Syntax Error at line {token.row}, column {token.col}: {message}")
        self.token = token

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def peek(self):

        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return Token('EOF', '', -1, -1)

    def advance(self):

        if self.current < len(self.tokens):
            self.current += 1
        return self.peek()

    def match(self, *token_types):

        if self.peek().type in token_types:
            current_token = self.peek()
            self.advance()
            return current_token
        return None

    def expect(self, token_type):

        token = self.match(token_type)
        if not token:
            raise ParserError(f"Expected token {token_type}", self.peek())
        return token

    def parse(self):

        return self.program()

    def program(self):

        statements = self.statement_list()
        return ASTNode('Program', statements)

    def statement_list(self):

        statements = []
        while self.peek().type != 'EOF' and self.peek().type != 'RIGHT_CURLY_BRACES':
            statement_node = self.statement()
            statements.append(statement_node)
        return statements
    
    def statement(self):

        current_token = self.peek()
        
        if current_token.type in {'INT_DATATYPE', 'DOUBLE_DATATYPE', 'BOOL_DATATYPE', 'CHAR_DATATYPE', 'STRING_DATATYPE'}:
            next_next_token = self.tokens[self.current + 2] if (self.current + 2) < len(self.tokens) else None
            if next_next_token and next_next_token.type == "LEFT_PARENTHESIS":
                return self.function_declaration()
            else:
                return self.variable_declaration()
        elif current_token.type == 'IF_KEYWORD':
            return self.if_statement()
        elif current_token.type == 'FOR_KEYWORD':
            return self.for_statement()
        elif current_token.type == 'WHILE_KEYWORD':
            return self.while_statement()
        elif current_token.type == 'RETURN_KEYWORD':
            return self.return_statement()
        elif current_token.type == 'IDENTIFIER':
            next_token = self.tokens[self.current + 1] if (self.current + 1) < len(self.tokens) else None
            if next_token and next_token.type == 'LEFT_PARENTHESIS':
                return self.function_call()
            elif next_token and next_token.type in {'ASSIGN_OPERATOR', 'PLUS_ASSIGN_OPERATOR', 'MINUS_ASSIGN_OPERATOR', 'MULTIPLY_ASSIGN_OPERATOR', 'DIVISION_ASSIGN_OPERATOR'}:
                return self.assignment()
            else:
                return self.expression_statement()
        else:
            return self.expression_statement()

    def function_declaration(self):
        global function_end_row
        return_type = self.match('INT_DATATYPE', 'DOUBLE_DATATYPE', 'BOOL_DATATYPE', 'CHAR_DATATYPE', 'STRING_DATATYPE')            
        return_type_node = ASTNode('Datatype', value = return_type.value)
        function_name = self.expect('IDENTIFIER')
        function_name_node = ASTNode('Identifier', value = function_name.value)
        self.expect('LEFT_PARENTHESIS')
        parameters_node = self.parameter_list()
        self.expect('RIGHT_PARENTHESIS')
        body_node = self.block()
        if body_node.children[-1].type != 'ReturnStatement':            
            raise SystemExit(f'Function has no return statement at line {function_end_row}')
        function_node = ASTNode('FunctionDeclaration', [return_type_node, function_name_node, parameters_node, body_node], row = self.peek().row, col = self.peek().col)
        return function_node

    def parameter_list(self):
        
        parameters = []
        if self.peek().type != 'RIGHT_PARENTHESIS':
            while True:
                datatype = self.match('INT_DATATYPE', 'DOUBLE_DATATYPE', 'BOOL_DATATYPE', 'CHAR_DATATYPE', 'STRING_DATATYPE')
                identifier = self.expect('IDENTIFIER')
                parameter_node = ASTNode('Parameter', [ASTNode('Datatype', value = datatype.value, row = datatype.row, col = datatype.col), ASTNode('Identifier', value = identifier.value, row = identifier.row, col = identifier.col)], row = self.peek().row, col = self.peek().col)
                parameters.append(parameter_node)
                if not self.match('COMMA_SYMBOL'):
                    break
        parameters_node = ASTNode('ParameterList', parameters, row = self.peek().row, col = self.peek().col)
        return parameters_node
    
    def function_call(self):
        
        token_before_call = self.tokens[self.current - 1].type if self.current - 1 >= 0 else None        
        function_name = self.expect('IDENTIFIER')
        function_name_node = ASTNode('Identifier', value = function_name.value, row = function_name.row, col = function_name.col)
        self.expect('LEFT_PARENTHESIS')
        arguments_node = self.argument_list()
        self.expect('RIGHT_PARENTHESIS')        
        if token_before_call is None or token_before_call == 'SEMICOLON_SYMBOL':
            self.expect('SEMICOLON_SYMBOL')
        # self.match('SEMICOLON_SYMBOL')
        function_call_node = ASTNode('FunctionCall', [function_name_node, arguments_node], row = self.peek().row, col = self.peek().col)
        return function_call_node

    def argument_list(self):

        arguments = []
        if self.peek().type != 'RIGHT_PARENTHESIS':
            while True:
                expression_node = self.expression()
                arguments.append(expression_node)
                if not self.match('COMMA_SYMBOL'):
                    break
        arguments_node = ASTNode('ArgumentList', arguments, row = self.peek().row, col = self.peek().col)
        return arguments_node

    def variable_declaration(self):
        
        datatype = self.match('INT_DATATYPE', 'DOUBLE_DATATYPE', 'BOOL_DATATYPE', 'CHAR_DATATYPE', 'STRING_DATATYPE')
        datatype_node = ASTNode('Datatype', value = datatype.value, row = datatype.row, col = datatype.col)
        identifier = self.expect('IDENTIFIER')
        identifier_node = ASTNode('Identifier', value = identifier.value, row = datatype.row, col = datatype.col)
        declaration_node = ASTNode('VariableDeclaration', [datatype_node, identifier_node], row = self.peek().row, col = self.peek().col)

        if self.match('ASSIGN_OPERATOR'):
            expression_node = self.expression()
            # assignment_node = ASTNode('AssignmentDeclaration', [expression_node], row = self.peek().row, col = self.peek().col)
            # declaration_node.children.append(assignment_node)
            declaration_node.children.append(expression_node)
        self.expect('SEMICOLON_SYMBOL')        
        return declaration_node

    def assignment(self):
        
        identifier = self.expect('IDENTIFIER')
        assign_type_operator = self.match('ASSIGN_OPERATOR', 'PLUS_ASSIGN_OPERATOR', 'MINUS_ASSIGN_OPERATOR', 'MULTIPLY_ASSIGN_OPERATOR', 'DIVISION_ASSIGN_OPERATOR')        
        if not assign_type_operator:
            raise ParserError("Expected assignment operator", self.peek())
        expression_node = self.expression()        
        # For Loop 3rd part fix
        token_curr_type = self.peek().type
        token_check_infront = self.tokens[self.current + 1] if self.current + 1 < len(self.tokens) else None
        """
        if (token_curr_type == 'SEMICOLON_SYMBOL' and token_check_infront.type == 'RIGHT_PARENTHESIS') or (token_curr_type == 'RIGHT_PARENTHESIS' and token_check_infront.type == 'LEFT_CURLY_BRACES'):
            #self.expect('SEMICOLON_SYMBOL')
            pera = -1
        else:
            self.expect('SEMICOLON_SYMBOL')
        """
        if token_check_infront is None:
            self.expect('SEMICOLON_SYMBOL')
        elif (token_curr_type != 'SEMICOLON_SYMBOL' or token_check_infront.type != 'RIGHT_PARENTHESIS') and (token_curr_type != 'RIGHT_PARENTHESIS' or token_check_infront.type != 'LEFT_CURLY_BRACES'):
            self.expect('SEMICOLON_SYMBOL')
        # self.expect('SEMICOLON_SYMBOL')
        identifier_node = ASTNode('Identifier', value = identifier.value, row = identifier.row, col = identifier.col)
        assign_type_operator_node = ASTNode('AssignTypeOperator', value = assign_type_operator.value, row = assign_type_operator.row, col = assign_type_operator.col)
        assignment_node = ASTNode('Assignment', [identifier_node, assign_type_operator_node, expression_node], row = self.peek().row, col = self.peek().col)
        return assignment_node        

    def if_statement(self):
        
        self.expect('IF_KEYWORD')
        self.expect('LEFT_PARENTHESIS')
        condition_node = self.expression()
        self.expect('RIGHT_PARENTHESIS')
        if_block_node = self.block()
        if_node = ASTNode('IfStatement', [condition_node, if_block_node], row = self.peek().row, col = self.peek().col)

        while self.match('ELIF_KEYWORD'):
            self.expect('LEFT_PARENTHESIS')
            elif_condition_node = self.expression()
            self.expect('RIGHT_PARENTHESIS')
            elif_block_node = self.block()
            elif_node = ASTNode('ElifStatement', [elif_condition_node, elif_block_node], row = self.peek().row, col = self.peek().col)
            if_node.children.append(elif_node)

        if self.match('ELSE_KEYWORD'):
            else_block_node = self.block()
            else_node = ASTNode('ElseStatement', [else_block_node], row = self.peek().row, col = self.peek().col)
            if_node.children.append(else_node)
        return if_node

    def for_statement(self):
        
        self.expect('FOR_KEYWORD')
        self.expect('LEFT_PARENTHESIS')

        if self.peek().type in {'INT_DATATYPE', 'DOUBLE_DATATYPE', 'BOOL_DATATYPE', 'CHAR_DATATYPE', 'STRING_DATATYPE'}:
            init_node = self.variable_declaration()
        elif self.peek().type != 'SEMICOLON_SYMBOL':
            init_node = self.assignment()
        else:
            init_node = ASTNode('Empty', row = self.peek().row, col = self.peek().col)
            self.expect('SEMICOLON_SYMBOL')
        # self.expect('SEMICOLON_SYMBOL')
        
        if self.peek().type != 'SEMICOLON_SYMBOL':
            condition_node = self.expression()
        else:
            condition_node = ASTNode('Empty', row = self.peek().row, col = self.peek().col)
        self.expect('SEMICOLON_SYMBOL')

        if self.peek().type != 'RIGHT_PARENTHESIS':
            increment_node = self.assignment()
        else:
            increment_node = ASTNode('Empty', row = self.peek().row, col = self.peek().col)
        self.expect('RIGHT_PARENTHESIS')
        body_node = self.block()
        for_node = ASTNode('ForStatement', [init_node, condition_node, increment_node, body_node], row = self.peek().row, col = self.peek().col)
        return for_node        

    def while_statement(self):
        
        self.expect('WHILE_KEYWORD')
        self.expect('LEFT_PARENTHESIS')
        condition_node = self.expression()
        self.expect('RIGHT_PARENTHESIS')
        body_node = self.block()
        while_node = ASTNode('WhileStatement', [condition_node, body_node], row = self.peek().row, col = self.peek().col)
        return while_node        

    def return_statement(self):
        
        self.expect('RETURN_KEYWORD')
        expression_node = self.expression()
        self.expect('SEMICOLON_SYMBOL')
        return ASTNode('ReturnStatement', [expression_node], row = self.peek().row, col = self.peek().col)

    def expression_statement(self):
        
        expression_node = self.expression()
        self.expect('SEMICOLON_SYMBOL')
        return ASTNode('ExpressionStatement', [expression_node], row = self.peek().row, col = self.peek().col)

    def block(self):
        global function_end_row
        self.expect('LEFT_CURLY_BRACES')
        statements = self.statement_list()
        # print(f'Row valjda: {self.peek().row} Column valjda: {self.peek().col}')
        function_end_row = self.peek().row
        self.expect('RIGHT_CURLY_BRACES')
        block_node = ASTNode('Block', statements, row = self.peek().row, col = self.peek().col)
        return block_node

    def expression(self):
        
        node = self.logical_or()
        return node

    def logical_or(self):
        
        node = self.logical_and()
        while self.match('OR_OPERATOR'):
            operator = '||'
            right_side = self.logical_and()
            node = ASTNode('LogicalOr', [node, ASTNode('Operator', value = operator, row = self.peek().row, col = self.peek().col), right_side], row = self.peek().row, col = self.peek().col)
        return node

    def logical_and(self):
        
        node = self.equality()
        while self.match('AND_OPERATOR'):
            operator = '&&'
            right_side = self.equality()
            node = ASTNode('LogicalAnd', [node, ASTNode('Operator', value = operator, row = self.peek().row, col = self.peek().col), right_side], row = self.peek().row, col = self.peek().col)
        return node

    def equality(self):
        
        node = self.comparison()        
        while True:
            # Posto moze vise od jedne operacije da zadovoljava pravilo, moramo da zapravo sacuvamo koja je ta operacija
            op = self.match('EQUALS_OPERATOR', 'NOT_EQUALS_OPERATOR')
            if op:
                operator = op.value
                right_side = self.comparison()
                node = ASTNode('Equality', [node, ASTNode('Operator', value = operator, row = self.peek().row, col = self.peek().col), right_side], row = self.peek().row, col = self.peek().col)
            else:
                break
        return node

    def comparison(self):
        
        node = self.term()
        while True:
            op = self.match('GREATER_OPERATOR', 'GREATER_EQUALS_OPERATOR', 'LESS_OPERATOR', 'LESS_EQUALS_OPERATOR')
            if op:
                operator = op.value
                right_side = self.term()
                node = ASTNode('Comparison', [node, ASTNode('Operator', value = operator, row = self.peek().row, col = self.peek().col), right_side], row = self.peek().row, col = self.peek().col)
            else:
                break
        return node

    def term(self):
        
        node = self.factor()
        while True:
            op = self.match('PLUS_OPERATOR', 'MINUS_OPERATOR')
            if op:
                operator = op.value
                right_side = self.factor()
                node = ASTNode('Term', [node, ASTNode('Operator', value = operator, row = self.peek().row, col = self.peek().col), right_side], row = self.peek().row, col = self.peek().col)
            else:
                break
        return node

    def factor(self):
        
        node = self.unary()
        while True:
            op = self.match('MULTIPLY_OPERATOR', 'DIVISION_OPERATOR', 'MODULO_OPERATOR')
            if op:
                operator = op.value
                right_side = self.unary()
                node = ASTNode('Factor', [node, ASTNode('Operator', value = operator, row = self.peek().row, col = self.peek().col), right_side], row = self.peek().row, col = self.peek().col)
            else:
                break
        return node

    def unary(self):        
        
        op = self.match('NOT_OPERATOR')
        if op:
            operator = '!'
            operand = self.unary()
            return ASTNode('Unary', [ASTNode('Operator', value = operator, row = self.peek().row, col = self.peek().col), operand], row = self.peek().row, col = self.peek().col)
        primary_node = self.primary()
        return primary_node

    def primary(self):
        
        token = self.peek()        
        if token.type in {'INT_LITERAL', 'DOUBLE_LITERAL', 'BOOL_LITERAL', 'CHAR_LITERAL', 'STRING_LITERAL'}:
            self.advance()
            return ASTNode('Literal', value = token.value, row = token.row, col = token.col)
        elif token.type == 'IDENTIFIER':
            next_token = self.tokens[self.current + 1] if (self.current + 1) < len(self.tokens) else None
            if next_token and next_token.type == 'LEFT_PARENTHESIS':
                return self.function_call()
            self.advance()
            return ASTNode('Identifier', value = token.value, row = token.row, col = token.col)
        elif token.type == 'LEFT_PARENTHESIS':
            self.advance()
            expression_node = self.expression()
            self.expect('RIGHT_PARENTHESIS')
            return ASTNode('Grouping', [expression_node], row = token.row, col = token.col)
        else:
            raise ParserError("Unexpected token in expression", token)
        

def adjust_tokens(tokens):
    
    new_tokens = []
    i = 0
    while i < len(tokens) - 1:
        curr_token = tokens[i]
        next_token = tokens[i + 1]
        if curr_token[0] == "COMMENT_LINE":
            i += 1
            continue
        elif curr_token[0] == "IDENTIFIER" and next_token[0] == "INCREMENT_OPERATOR":
            new_tokens.append(curr_token)
            new_tokens.append(("ASSIGN_OPERATOR", "=", -1, -1))
            new_tokens.append((curr_token[0], curr_token[1], -1, -1))
            new_tokens.append(("PLUS_OPERATOR", "+", -1, -1))
            new_tokens.append(("INT_LITERAL", "1", -1, -1))
            i += 2
        elif curr_token[0] == "IDENTIFIER" and next_token[0] == "DECREMENT_OPERATOR":
            new_tokens.append(curr_token)
            new_tokens.append(("ASSIGN_OPERATOR", "=", -1, -1))
            new_tokens.append((curr_token[0], curr_token[1], -1, -1))
            new_tokens.append(("MINUS_OPERATOR", "-", -1, -1))
            new_tokens.append(("INT_LITERAL", "1", -1, -1))
            i += 2
        elif curr_token[0] == "DOUBLE_LITERAL":
            bonus = ""
            if curr_token[1][-1] == ".":
                bonus = "0"
                # new_tokens.append((curr_token[0], curr_token[1] + "0", -1, -1))
            new_tokens.append((curr_token[0], curr_token[1] + bonus, -1, -1))
            i += 1
        else:
            new_tokens.append(curr_token)
            i += 1
    if tokens[i][0] != "COMMENT_LINE":
        new_tokens.append(tokens[i])    
    return new_tokens