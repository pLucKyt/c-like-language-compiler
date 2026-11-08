import re

TOKENS = {    
    # "INT_DATATYPE": r"int",
    # "INT_LITERAL": r"(-)?(0|[1-9][0-9]*)",
    "DOUBLE_DATATYPE": r"double",
    "DOUBLE_LITERAL": r"(-)?(0|[1-9][0-9]*)\.[0-9]*",
    "INT_DATATYPE": r"int",
    "INT_LITERAL": r"(-)?(0|[1-9][0-9]*)",
    "BOOL_DATATYPE": r"bool",
    "BOOL_LITERAL": r"true|false",
    "CHAR_DATATYPE": r"char",
    "CHAR_LITERAL": r"'(.|\\n|\\t|\\r)'",
    "STRING_DATATYPE": r"string",
    "STRING_LITERAL": r"\".*\"",
    "LEFT_SQUARE_BRACKET": r"\[",
    "RIGHT_SQUARE_BRACKET": r"\]",
    "LEFT_PARENTHESIS": r"\(",
    "RIGHT_PARENTHESIS": r"\)",
    "LEFT_CURLY_BRACES": r"\{",
    "RIGHT_CURLY_BRACES": r"\}",
    # "MAIN_FUNCTION": r"main",
    "COMMENT_LINE": r"#.*(\n)",
    "PLUS_ASSIGN_OPERATOR": r"\+=",
    "MINUS_ASSIGN_OPERATOR": r"\-=",
    "MULTIPLY_ASSIGN_OPERATOR": r"\*=",
    "DIVISION_ASSIGN_OPERATOR": r"\/=",
    "INCREMENT_OPERATOR": r"\+\+",
    "DECREMENT_OPERATOR": r"\-\-",
    "EQUALS_OPERATOR": r"==",
    "GREATER_EQUALS_OPERATOR": r">=",
    "LESS_EQUALS_OPERATOR": r"<=",
    "NOT_EQUALS_OPERATOR": r"!=",
    "ASSIGN_OPERATOR": r"=",
    "PLUS_OPERATOR": r"\+",
    "MINUS_OPERATOR": r"\-",
    "MULTIPLY_OPERATOR": r"\*",
    "DIVISION_OPERATOR": r"\/",
    "MODULO_OPERATOR": r"%",
    "GREATER_OPERATOR": r">",
    "LESS_OPERATOR": r"<",    
    "NOT_OPERATOR": r"!",
    "AND_OPERATOR": r"&&",
    "OR_OPERATOR": r"\|\|",
    "IF_KEYWORD": r"if",
    "ELIF_KEYWORD": r"elif",
    "ELSE_KEYWORD": r"else",
    "FOR_KEYWORD": r"for",
    "WHILE_KEYWORD": r"while",
    "RETURN_KEYWORD": r"return",    
    "NULL_VALUE": r"null",
    "COMMA_SYMBOL": r",",
    "SEMICOLON_SYMBOL": r";",    
    "IDENTIFIER": r"[a-zA-Z][_a-zA-Z0-9]*"
}

def extract_tokens(source_code):
    
    tokens = []
    i = 0
    buffer = ""
    curr_row = 1
    curr_col = 1
    # Base case for TOKEN_TYPE, TOKEN_VALUE
    current_token = ["NaN", ""]
    while i < len(source_code):
        found = False
        go_back = False
        if not(buffer == "" and source_code[i].isspace()):
            buffer += source_code[i]
        for key, val in TOKENS.items():
            if re.fullmatch(val, buffer):
                current_token[0] = key
                current_token[1] = buffer
                found = True
                break
        if current_token[0] != "NaN" and not found:
            tokens.append((current_token[0], current_token[1], curr_row, curr_col - len(current_token[1])))
            buffer = ""
            current_token[0] = "NaN"
            current_token[1] = ""
            # i -= 1
            go_back = True
            curr_col -= 1
        if not go_back and source_code[i] == '\n':
            curr_row += 1
            curr_col = 1
        elif source_code[i] == '\t':
            curr_col += 4
        else:
            curr_col += 1
        if not go_back:
            i += 1
    if not(current_token[0] == "NaN" and buffer == ""):
        if current_token[0] == "NaN":
            bad_token_start = len(source_code) - len(buffer)
            last_token_end = source_code[0:bad_token_start].rfind(tokens[-1][1])
            clutter = source_code[last_token_end:bad_token_start]
            num_of_newline = len(re.findall(r"\n", clutter))
            if num_of_newline:
                tokens.append((current_token[0], buffer, tokens[-1][2] + num_of_newline, bad_token_start - source_code[0:bad_token_start].rfind("\n")))
            else:
                tokens.append((current_token[0], buffer, tokens[-1][2], tokens[-1][3] + bad_token_start - last_token_end))
        else:
            tokens.append((current_token[0], buffer, curr_row, curr_col - len(current_token[1])))
    return tokens

def check_correctness(tokens):
    
    if tokens[-1][0] == "NaN":
        print(f'Error in line {tokens[-1][2]}, column {tokens[-1][3]}')
        return 1
    else:
        i = 0
        while i < len(tokens) - 1:
            curr_token = tokens[i]
            next_token = tokens[i + 1]
            if curr_token[0] != "IDENTIFIER" and (next_token[0] == "INCREMENT_OPERATOR" or next_token[0] == "DECREMENT_OPERATOR"):
                print(f'Error in line {next_token[2]}, column {next_token[3]}')
                return 1
            i += 1        
    print("Code is properly analyzed without bad tokens")
    return 0