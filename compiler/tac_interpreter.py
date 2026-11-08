from lexer import *
import os

source_code = ""
PATH_TO_CODE = os.getcwd() + "\\" + "intermediate_code.txt"

code_lines_arr = []
parameter_stack = []
jump_index_dict = {}
variable_scopes = []
main_index = None

def extract_code():
    global source_code
    with open(PATH_TO_CODE, "r") as file:
        source_code = file.read()
    return

def slice_lines():
    global source_code, code_lines_arr
    code_lines_arr = source_code.splitlines()
    return

def analyze_lines():
    global code_lines_arr, jump_index_dict, main_index
    i = 0
    for line in code_lines_arr:        
        if line == "FUNCTION main":
            main_index = i
        elif re.fullmatch(r"FUNCTION [a-zA-Z][_a-zA-Z0-9]*", line):
            function_name = line.split(" ")[1]            
            jump_index_dict[function_name] = i
        elif re.fullmatch(r"~L[1-9][0-9]*", line):
            label_name = line.split("~")[1]            
            jump_index_dict[label_name] = i
        i += 1
    return

def use_variable(variable_name):
    global variable_scopes
    for scope in reversed(variable_scopes):
        if variable_name in scope:
            return scope[variable_name]    
    return type_cleanup(variable_name)

def change_variable(variable_name, val):
    global variable_scopes    
    for scope in reversed(variable_scopes):
        if variable_name in scope:
            scope[variable_name] = val
            return
    print("Ako dodje ovde za menjanje postojece promenljive, ovo bas nije dobro")
    return

def split_properly(line):

    arr = []
    # Implementation
    i = 0
    buffer = ""
    truth = True
    while i < len(line):
        if line[i] == "\"" or line[i] == "\'":
            buffer += line[i]
            truth = not truth
        elif line[i] == " " and truth:
            arr.append(buffer)
            buffer = ""
        else:
            buffer += line[i]
        i += 1
    arr.append(buffer)
    return arr

def type_cleanup(s):

    if re.fullmatch(r"\".*\"", s):
        return s[1:-1]
    if re.fullmatch(r"\'.\'", s):
        return s[1]
    if s == "true":
        return True
    if s == "false":
        return False
    if re.fullmatch(r"(-)?(0|[1-9][0-9]*)", s):
        return int(s)
    if re.fullmatch(r"(-)?(0|[1-9][0-9]*)\.[0-9]*", s):
        return float(s)
    return s

def eval_bin(x, operator, y):
    
    if operator == "||":
        if x or y:
            return 1
        return 0
    if operator == "&&":
        if x and y:
            return 1
        return 0
    if operator == "==":
        if x == y:
            return 1
        return 0
    if operator == "!=":
        if x != y:
            return 1
        return 0
    if operator == ">":
        if x > y:
            return 1
        return 0
    if operator == ">=":
        if x >= y:
            return 1
        return 0
    if operator == "<":
        if x < y:
            return 1
        return 0
    if operator == "<=":
        if x <= y:
            return 1
        return 0
    if operator == "+":
        if isinstance(x, str) and (isinstance(y, int) or isinstance(y, float)):
            return x + str(y)
        return x + y
    if operator == "-":        
        return x - y
    if operator == "*":        
        return x * y
    if operator == "/":
        return x / y
    if operator == "%":
        return x % y
    return

def eval_unary(x):
    
    if x == "false" or x == 0 or x == 0.0 or x == "":
        return True
    return False

def traverse_lines(iterator):
    global code_lines_arr, parameter_stack, jump_index_dict, variable_scopes, main_index
    # Poziv za global nece uticati na poziv za main, zato sto main nikada nece dodirnuti FUNCTION name niti bilo koju liniju vezanu za globalne promenljive
    while iterator < len(code_lines_arr):
        # FUNCTION DECLARATION
        # print(code_lines_arr[iterator])
        if re.fullmatch(r"FUNCTION [a-zA-Z][_a-zA-Z0-9]*", code_lines_arr[iterator]):
            while True:
                if code_lines_arr[iterator] == "ENDFUNCTION":
                    break
                iterator += 1
        # RETURN
        elif re.fullmatch(r"RETURN .*", code_lines_arr[iterator]):            
            function_arr = split_properly(code_lines_arr[iterator])
            function_result = function_arr[1]
            # Ovo ce biti provera da li je promenljiva ili literal i na osnovu toga cemo da pristupimo globalnom dictionary-u za promenljive            
            if re.fullmatch(r"[a-zA-Z][_a-zA-Z0-9]*", function_result):
                return use_variable(function_result)
            # Mozda cemo morati isto onaj type check da konvertujemo string u int/double
            return type_cleanup(function_result)

        # PARAM
        elif re.fullmatch(r"PARAM .*", code_lines_arr[iterator]):            
            param_arr = split_properly(code_lines_arr[iterator])
            param_arr.pop(0)
            param_arr.reverse()
            i = len(parameter_stack) - 1
            for param in param_arr:                
                variable_scopes[-1][param] = parameter_stack[i]
                i -= 1
        # CALL
        elif re.fullmatch(r"CALL .*", code_lines_arr[iterator]):            
            call_arr = split_properly(code_lines_arr[iterator])
            function_name = call_arr[1]
            # Ovde samo moze print jer nas input mora da bude dodeljen nekoj promenljivoj
            if function_name == "print":                
                print(parameter_stack[-1])
            else:
                variable_scopes.append({})
                variable_val = traverse_lines(jump_index_dict[function_name] + 1)
                variable_scopes.pop()
        # PUSH
        elif re.fullmatch(r"PUSH .*", code_lines_arr[iterator]):            
            push_arr = split_properly(code_lines_arr[iterator])
            push_arr.pop(0)
            for arg in push_arr:                
                parameter_stack.append(use_variable(arg))
        # POP
        elif re.fullmatch(r"POP .*", code_lines_arr[iterator]):            
            pop_arr = split_properly(code_lines_arr[iterator])
            pop_num = int(pop_arr[1])
            while pop_num > 0:
                parameter_stack.pop()
                pop_num -= 1
        # IF
        elif re.fullmatch(r"IF .*", code_lines_arr[iterator]):            
            if_arr = split_properly(code_lines_arr[iterator])
            if use_variable(if_arr[1]) == 0:
                iterator = jump_index_dict[if_arr[5][1:]] + 1
                continue
            variable_scopes.append({})
        # GOTO
        elif re.fullmatch(r"GOTO .*", code_lines_arr[iterator]):            
            goto_arr = split_properly(code_lines_arr[iterator])
            iterator = jump_index_dict[goto_arr[1][1:]] + 1            
            variable_scopes.pop()
            continue        
        # DECLARE i obican assignment
        elif re.fullmatch(r"DECLARE .*", code_lines_arr[iterator]) or re.fullmatch(r"[a-zA-Z][_a-zA-Z0-9]* .*", code_lines_arr[iterator]):            
            declare_arr = split_properly(code_lines_arr[iterator])
            if re.fullmatch(r"DECLARE .*", code_lines_arr[iterator]):
                declare_arr.pop(0)
            variable_name = declare_arr[0]
            variable_val = None            
            if declare_arr[2] == "CALL":                
                if declare_arr[3] == "input_i" or declare_arr[3] == "input_d" or declare_arr[3] == "input_s":
                    variable_val = input()                    
                    variable_val = type_cleanup(variable_val)
                else:
                    variable_scopes.append({})                    
                    variable_val = traverse_lines(jump_index_dict[declare_arr[3]] + 1)
                    variable_scopes.pop()
            elif len(declare_arr) == 5:
                # Binarna operacija
                x_operator = declare_arr[2]
                y_operator = declare_arr[4]
                variable_val = eval_bin(use_variable(x_operator), declare_arr[3], use_variable(y_operator))
            elif re.fullmatch(r"!.*", declare_arr[2]):
                # Unarna operacija
                x_operator = declare_arr[2][1:]
                variable_val = eval_unary(use_variable(x_operator))
                return
            else:
                # Literal
                variable_val = type_cleanup(declare_arr[2])            
            if re.fullmatch(r"DECLARE .*", code_lines_arr[iterator]) or re.fullmatch(r"t[1-9][0-9]*", variable_name):
                variable_scopes[-1][variable_name] = variable_val
            else:                              
                variable_on_variable = split_properly(code_lines_arr[iterator])               
                if len(variable_on_variable) == 3 and re.fullmatch(r"[a-zA-Z][_a-zA-Z0-9]*", variable_on_variable[0]) and re.fullmatch(r"[a-zA-Z][_a-zA-Z0-9]*", variable_on_variable[2]):                    
                    change_variable(variable_name, use_variable(variable_val))
                else:
                    change_variable(variable_name, variable_val)
        iterator += 1    
    return

def global_stuff():
    global variable_scopes
    variable_scopes.append({})
    traverse_lines(0)
    return

def main_stuff():
    global main_index
    variable_scopes.append({})
    traverse_lines(main_index + 1)
    return

def interprete_code():
    global code_lines_arr, main_index
    extract_code()
    slice_lines()    
    analyze_lines()
    global_stuff()    
    main_stuff()
    return
