from lexer import *
from parser import *
from tree import *
from tac_interpreter import *
import os

source_code = ""
temporary_counter = 1
label_counter = 1
PATH_TO_CODE = os.getcwd() + "\\" + "intermediate_code.txt"

def function_call_helper(argument_list):

    if not len(argument_list):
        return None
    push_string = f'PUSH '
    for x in argument_list:
        push_string += x + " "
    push_string = push_string[:-1]
    return push_string
    
def break_expression(node):
    global temporary_counter, source_code
    # Izlaz iz rekurzije je kada je operand promenljiva ili literal
    if node.type == 'Identifier' or node.type == 'Literal':
        # print(f't{temporary_counter} = {node.value}')
        return node.value
    if node.type == 'Grouping':
        sus = break_expression(node.children[0])
        return f't{temporary_counter - 1}'
    if node.type == 'FunctionCall':
        sus_list = []
        for arg_node in node.children[1].children:
            sus = break_expression(arg_node)
            sus_list.append(sus)
        # push_string, new_function_string = function_call_helper(sus_list, node.children[0].value)
        push_string = function_call_helper(sus_list)
        if push_string:
            source_code += push_string + '\n'
        # source_code += f't{temporary_counter} = {new_function_string}' + '\n'
        source_code += f't{temporary_counter} = CALL {node.children[0].value}' + '\n'
        if len(sus_list):
            source_code += f'POP {len(sus_list)}' + '\n'
    elif node.type == 'Unary':
        sus = break_expression(node.children[1])
        # print(f't{temporary_counter} = {node.children[0].value}{sus}')
        source_code += f't{temporary_counter} = {node.children[0].value}{sus}' + '\n'
    else:
        sus1 = break_expression(node.children[0])
        sus2 = break_expression(node.children[2])
        # print(f't{temporary_counter} = {sus1} {node.children[1].value} {sus2}')
        source_code += f't{temporary_counter} = {sus1} {node.children[1].value} {sus2}' + '\n'
    temporary_counter += 1
    return f't{temporary_counter - 1}'
    
def fix_assignment(node_identifier, node_operator):
    global temporary_counter, source_code
    # index = source_code.rfind(node_identifier)
    index = source_code.rfind(node_identifier + " ")
    shungite = source_code[index:]
    source_code = source_code[:index]
    # information = shungite.split(" ")
    information = split_properly(shungite)
    new_operator = node_operator[0]
    # Ako je assignment sa dva operanda sa desne strane jednakosti
    if len(information) == 5:
        # print(f't{temporary_counter} = {information[2]} {information[3]} {information[4]}')
        source_code += f't{temporary_counter} = {information[2]} {information[3]} {information[4]}'
        temporary_counter += 1
        # print(f'{node_identifier} = {node_identifier} {new_operator} t{temporary_counter - 1}')
        source_code += f'{node_identifier} = {node_identifier} {new_operator} t{temporary_counter - 1}' + '\n'
    # Ako je assignment sa samo jednim operandom sa desne strane jednakosti
    elif len(information) == 3:
        # print(f'{node_identifier} = {node_identifier} {new_operator} {information[2]}')
        source_code += f'{node_identifier} = {node_identifier} {new_operator} {information[2]}'
    return

def f_replace(identifier, t_val):
    global temporary_counter, source_code    
    const_regexes = [TOKENS["DOUBLE_LITERAL"], TOKENS["INT_LITERAL"], TOKENS["BOOL_LITERAL"], TOKENS["CHAR_LITERAL"], TOKENS["STRING_LITERAL"]]
    for regex in const_regexes:
        if re.fullmatch(regex, t_val):
            source_code += f'{identifier} = {t_val}' + '\n'
            return
    if not re.fullmatch(r"t[1-9][0-9]*", t_val):
        source_code += identifier + " = " + t_val + '\n'
        return
    index = source_code.rfind(t_val)
    if index != -1:
        source_code = source_code[:index] + identifier + source_code[index + len(t_val):]
        temporary_counter -= 1
    else:
        source_code += f'{identifier} = {t_val}' + '\n'
    # temporary_counter -= 1
    return

def determine_const(datatype):

    if datatype == "int":
        return 0
    if datatype == "double":
        return 0.0
    if datatype == "string":
        return "\"\""
    if datatype == "char":
        return "\'0\'"
    if datatype == "bool":
        return "False"    
    return

def traverse_ast(node):
    global temporary_counter, label_counter, source_code
    if node.type == 'VariableDeclaration':
        if len(node.children) == 3:
            sus = break_expression(node.children[2])
            f_replace(node.children[1].value, sus)            
            # Da ne proguta nesto ispred promenljive, ovaj razmak nam to garantuje
            index = source_code.rfind(node.children[1].value + " =")
            source_code = source_code[:index] + f'DECLARE {node.children[1].value}' + source_code[index + len(node.children[1].value):]
        else:
            neutral_const = determine_const(node.children[0].value)
            source_code += f'DECLARE {node.children[1].value} = {neutral_const}' + '\n'
        # Mora prolaz jer se moze naci function call
        return
    if node.type == 'Assignment':
        sus = break_expression(node.children[2])        
        f_replace(node.children[0].value, sus)        
        if node.children[1].value != "=":
            fix_assignment(node.children[0].value, node.children[1].value)
        return
    if node.type == 'FunctionDeclaration':
        source_code += f'FUNCTION {node.children[1].value}' + '\n'
        omE = 0
        for param_node in node.children[2].children:
            if omE == 0:
                source_code += f'PARAM {param_node.children[1].value}'
            else:                
                source_code += f' {param_node.children[1].value}'
            omE += 1
        if omE:
            source_code += '\n'
        for child_node in node.children[3].children:
            traverse_ast(child_node)
        source_code += f'ENDFUNCTION' + '\n'
        return
    if node.type == 'FunctionCall':
        argument_names = []
        for arg_node in node.children[1].children:
            sus = break_expression(arg_node)
            argument_names.append(sus)              
        push_string = function_call_helper(argument_names)
        if push_string:
            source_code += push_string + '\n'        
        source_code += f'CALL {node.children[0].value}' + '\n'
        source_code += f'POP {len(argument_names)}' + '\n'
        return
    if node.type == 'ReturnStatement':
        sus = break_expression(node.children[0])
        source_code += f'RETURN {sus}' + '\n'
        return
    if node.type == 'IfStatement':
        # Label kad je if u if-u mora da se drugacije numerise
        num_of_statements = len(node.children) - 1
        sus = break_expression(node.children[0])
        entry_num = label_counter
        if num_of_statements == 1:
            source_code += f'IF {sus} == 0 GOTO ~L{entry_num + 1}' + '\n'
        else:
            source_code += f'IF {sus} == 0 GOTO ~L{entry_num}' + '\n'
        label_counter += 1
        exit_num = label_counter
        # label_counter += 1
        for child_node in node.children[1].children:
            traverse_ast(child_node)
        # !!!        
        source_code += f'GOTO ~L{exit_num}' + '\n'
        i = 2
        while i < len(node.children):
            source_code += f'~L{entry_num}' + '\n'
            if node.children[i].type == 'ElifStatement':
                sus_xd = break_expression(node.children[i].children[0])                
                source_code += f'IF {sus_xd} == 0 GOTO ~L{label_counter}' + '\n'
                entry_num = label_counter
                label_counter += 1
                for child_node in node.children[i].children[1].children:
                    traverse_ast(child_node)
                source_code += f'GOTO ~L{exit_num}' + '\n'
            else:
                label_counter += 1
                for child_node in node.children[i].children[0].children:
                    traverse_ast(child_node)
            i += 1
        source_code += f'~L{exit_num}' + '\n'
    if node.type == 'ForStatement':        
        if node.children[0].type != 'Empty':
            traverse_ast(node.children[0])
        label_counter += 1
        source_code += f'~L{label_counter}' + '\n'
        # label_counter += 1
        jump_back_num = label_counter
        label_counter += 1        
        sus = break_expression(node.children[1])
        source_code += f'IF {sus} == 0 GOTO ~L{label_counter}' + '\n'
        jump_out_num = label_counter
        label_counter += 1
        for child_node in node.children[3].children:
            traverse_ast(child_node)
        traverse_ast(node.children[2])
        source_code += f'GOTO ~L{jump_back_num}' + '\n'
        source_code += f'~L{jump_out_num}' + '\n'
    if node.type == 'WhileStatement':
        source_code += f'~L{label_counter}' + '\n'
        jump_back_num = label_counter
        label_counter += 1
        sus = break_expression(node.children[0])
        source_code += f'IF {sus} == 0 GOTO ~L{label_counter}' + '\n'
        jump_out_num = label_counter
        label_counter += 1
        for child_node in node.children[1].children:
            traverse_ast(child_node)
        source_code += f'GOTO ~L{jump_back_num}' + '\n'
        source_code += f'~L{jump_out_num}' + '\n'
    if node.type == 'Program':
        for child_node in node.children:
            traverse_ast(child_node)
    return

def save_result():
    global source_code
    with open(PATH_TO_CODE, "w") as file:
        file.write(source_code)
    return

def generate_code(ast):
    global source_code
    traverse_ast(ast)
    save_result()
    return
