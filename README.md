# Compiler for a C-like language

A compiler for a small C-like language, written in Python without any parser
libraries. Course project for Programski prevodioci (compilers).

Each stage is its own file:

- `lexer.py` turns the source text into tokens
- `parser.py` is a recursive descent parser that builds a syntax tree (`tree.py`)
- `semantics.py` does the static checks, types and scopes
- `tac_generator.py` emits three address code
- `tac_interpreter.py` runs that three address code

The language rules I was working to are in `docs/language-rules.txt` and the semantic
rules in `docs/semantic-analysis.txt`. There are eleven test programs in
`compiler/Testing codes/`.

## Running

    python compiler/run.py

It asks for the source file name.
