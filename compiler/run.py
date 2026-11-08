import os
from lexer import *
from parser import *
from semantics import *
from tac_generator import *
from tac_interpreter import *

PATH_TO_CODES = os.getcwd() + "\\" + "Testing codes"
PATH_TO_LIB = os.getcwd() + "\\" + "lib.txt"
source_code = ""
token_info = []

def extract_code(file_name):
    global source_code
    file_path = PATH_TO_CODES + "\\" + file_name
    print(file_path)
    with open(file_path, "r") as file:
        # source_code = ""
        source_code = file.read()        
    return

def extract_lib():
    
    lib = ""
    with open(PATH_TO_LIB, "r") as file:
        lib = file.read()
    return lib

def print_tokens():
    global token_info
    print("TOKEN TYPE: TOKEN VALUE ~~~ ROW, COLUMN")
    for token in token_info:
        print(f'{token[0]}: {token[1]} ~~~ {token[2]}, {token[3]}')
    return

def sussy(tokens):
    tokens_new = []
    for token in tokens:
        tokens_new.append(Token(token[0], token[1], token[2], token[3]))

    if tokens_new[-1][0] != "NaN":
        parser = Parser(tokens_new)
        try:
            ast = parser.parse()
            print(ast)
        except ParserError as e:
            print(e)
            sys.exit(1)
    else:
        print("Cannot parse due to lexical errors.")
        sys.exit(1)
    print("Semanticka xd")
    semantic_analysis(ast)
    print("Prosla semanticka xd")
    generate_code(ast)
    interprete_code()
    return

def main():    
    global source_code, token_info    
    file_name = input("Enter file name:\n")
    lib = extract_lib()
    extract_code(file_name)
    source_code = lib + source_code    
    token_info = extract_tokens(source_code)    
    print_tokens()
    if check_correctness(token_info):
        return    
    token_info = adjust_tokens(token_info)
    print_tokens()
    sussy(token_info)
    return

main()