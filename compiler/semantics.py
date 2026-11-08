from lexer import *
from parser import *
from tree import *
import sys

class SymbolTable:
    def __init__(self):
        self.scope_stack = []
        self.enter_scope()

    def enter_scope(self):

        self.scope_stack.append({})
        return

    def exit_scope(self):
        
        self.scope_stack.pop()
        return 

    def declare_variable(self, variable_name, variable_type, row, col):

        if variable_name in self.scope_stack[-1]:
            print(f'Variable {variable_name} already declared in the current scope at row: {row}, col: {col}')
            sys.exit(1)
        self.scope_stack[-1][variable_name] = [variable_name, variable_type]
        return
    
    def use_variable(self, variable_name, row, col):

        for scope in reversed(self.scope_stack):
            if variable_name in scope:
                return scope[variable_name]
        print(f'Variable {variable_name} used before declaration at row: {row}, col: {col}')
        sys.exit(1)
        return

symbol_table = SymbolTable()
function_table = {}
function_return_arr = []

def special_type_check(var1, var2):

    if var1 == var2:
        return True
    if var1 in ['int', 'char'] and var2 in ['int', 'char']:
        return True
    if var1 in ['int', 'bool'] and var2 in ['int', 'bool']:
        return True
    return False

def literal_type(node):

    datatype = None
    for key, val in TOKENS.items():
        if re.fullmatch(val, node.value):
            datatype = key
            break
    if datatype == "INT_LITERAL":
        return 'int'
    elif datatype == "DOUBLE_LITERAL":
        return 'double'
    elif datatype == "BOOL_LITERAL":
        return 'bool'
    elif datatype == "CHAR_LITERAL":
        return 'char'
    elif datatype == "STRING_LITERAL":
        return 'string'
    print("Literal greska vrv xd")
    return None

def find_operation_type(node):

    # Izlaz iz rekurzije je kada su parametri identifier-i ili literali
    if node.type == 'Identifier':
        attr = symbol_table.use_variable(node.value, node.row, node.col)
        return attr[1]
    elif node.type == 'FunctionCall':
        attr = symbol_table.use_variable(node.children[0].value, node.row, node.col)
        return attr[1]
    elif node.type == 'Literal':
        # Regex gluposti
        return literal_type(node)
    # Poseban slucaj kada node ima samo jedan parametar
    if node.type == 'Unary':
        op_type = find_operation_type(node.children[1])
        if op_type != 'int' and op_type != 'bool':
            print(f'Bad type for unary operation at row: {node.row}, col: {node.col}')
            sys.exit(1)
        return op_type
    elif node.type == 'Grouping':
        return find_operation_type(node.children[0])
    # Operacije koje imaju razlicite simbole i dva operanda
    first_operand = find_operation_type(node.children[0])
    second_operand = find_operation_type(node.children[2])
    if node.type == 'LogicalOr' or node.type == 'LogicalAnd':
        if first_operand not in ['bool', 'int'] or second_operand not in ['bool', 'int']:
            print(f'Bad type for logical operation at row: {node.row}, col: {node.col}')
            sys.exit(1)
        return 'bool'
    elif node.type == 'Equality' or node.type == 'Comparison':
        if first_operand != second_operand:
            print(f'Bad type for equality/comparison operation at row: {node.row}, col: {node.col}')
            sys.exit(1)
        return first_operand
    elif node.type == 'Term':
        if first_operand == second_operand and first_operand in ['int', 'double']:
            return first_operand
        if first_operand == 'int' and second_operand == 'char':
            return 'int'
        if first_operand == 'int' and second_operand == 'bool':
            return 'bool'
        if first_operand == 'char' and second_operand == 'int':
            return 'char'
        if first_operand == 'string' and second_operand == 'char' and node.children[1].value == '+':
            return 'string'
        if first_operand == 'string' and second_operand == 'int' and node.children[1].value == '+':
            return 'string'
        if first_operand == 'string' and second_operand == 'double' and node.children[1].value == '+':
            return 'string'
        if first_operand == second_operand and first_operand == 'string' and node.children[1].value == '+':
            return 'string'
        print(f'Bad type for term operation at row: {node.row}, col: {node.col}')
        sys.exit(1)
    elif node.type == 'Factor':        
        if first_operand == second_operand and first_operand == 'double' and node.children[1].value != '%':
            return 'double'        
        if (first_operand == second_operand and first_operand == 'int') or (first_operand == 'int' and second_operand == 'bool'):
            return 'int'        
        print(f'Bad type for factor operation at row: {node.row}, col: {node.col}')
        sys.exit(1)
    print("Ako je stigao dovde, nisam dobro uhvatio neku operaciju xd")
    return None

def traverse_ast(node):
    global symbol_table, function_table, function_return_arr 
    # symbol_table = SymbolTable()
    # Pre nego sto udjemo i proverimo ostale node-ove koji su deca trenutnom, moramo da vidimo kakvog je tipa trenutni node i da na osnovu toga dodamo scope ili uhvatimo gresku itd.
    if node.type == 'FunctionDeclaration':
        function_name = node.children[1].value
        function_return_type = node.children[0].value
        symbol_table.declare_variable(function_name, function_return_type, node.row, node.col)
        parameter_types = []
        for x in node.children[2].children:
            parameter_types.append(x.children[0].value)
        function_table[function_name] = parameter_types
        symbol_table.enter_scope()
    elif node.type == 'Parameter':
        parameter_name = node.children[1].value
        parameter_type = node.children[0].value
        symbol_table.declare_variable(parameter_name, parameter_type, node.row, node.col)
    elif node.type == 'ReturnStatement':
        return_type = find_operation_type(node.children[0])
        function_return_arr.append([return_type, node.row, node.col])
    elif node.type == 'ForStatement' or node.type == 'WhileStatement' or node.type == 'IfStatement' or node.type == 'ElifStatement' or node.type == 'ElseStatement':
        symbol_table.enter_scope()
    
    for child_node in node.children:
        traverse_ast(child_node)

    # Kada se zavrsi prolaz kroz node koji ima blok u sebi, hocemo da skinemo jedan scope sa stack-a
    if node.type == 'FunctionDeclaration' or node.type == 'ForStatement' or node.type == 'WhileStatement' or node.type == 'IfStatement' or node.type == 'ElifStatement' or node.type == 'ElseStatement':
        symbol_table.exit_scope()
    
    if node.type == 'VariableDeclaration' and len(node.children) == 3:
        identifier_datatype = node.children[0].value
        # expression_datatype = find_operation_type(node.children[2].children[0])
        expression_datatype = find_operation_type(node.children[2])
        if not special_type_check(identifier_datatype, expression_datatype):
            print(f'At declaration, the variable and assignment value are not of same or appropriate type at row: {node.row}, col: {node.col}')
            sys.exit(1)
    if node.type == 'VariableDeclaration':
        variable_name = node.children[1].value
        variable_type = node.children[0].value
        symbol_table.declare_variable(variable_name, variable_type, node.row, node.col)
    if node.type == 'Assignment':
        identifier_node = node.children[0]
        attr = symbol_table.use_variable(identifier_node.value, identifier_node.row, identifier_node.col)
        identifier_datatype = attr[1]
        expression_datatype = find_operation_type(node.children[2])        
        if not special_type_check(identifier_datatype, expression_datatype):
            print(f'At assignment, the variable and assignment value are not of same or appropriate type at row: {node.row}, col: {node.col}')
            sys.exit(1)
    if node.type == 'FunctionCall':
        function_parameter_types = function_table[node.children[0].value] if node.children[0].value in function_table else None
        if function_parameter_types is None:
            print(f'The function {node.children[0].value} doesn\'t exist at row : {node.children[0].row}, col: {node.children[0].col}')
            sys.exit(1)
        function_argument_types = []
        for x in node.children[1].children:
            function_argument_types.append(find_operation_type(x))
        if len(function_parameter_types) != len(function_argument_types):
            print(f'Function call {node.children[0].value} doesn\'t have valid argument number at row: {node.row}, col: {node.col}')
            sys.exit(1)
        i = 0
        while i < len(function_parameter_types):
            if function_parameter_types[i] != function_argument_types[i]:
                print(f'Function call {node.children[0].value} doesn\'t have valid argument types at row: {node.row}, col: {node.col}')
                sys.exit(1)
            i += 1
    if node.type == 'FunctionDeclaration':
        attr = symbol_table.use_variable(node.children[1].value, node.row, node.col)
        actual_return_type = attr[1]
        for x in function_return_arr:
            if not special_type_check(actual_return_type, x[0]):
                print(f'Bad return type for function {node.children[1].value} at row: {x[1]}, col: {x[2]}')
                sys.exit(1)
        function_return_arr = []
    return

def semantic_analysis(ast):    
    traverse_ast(ast)
    return
