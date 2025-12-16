from lexer import MyLexer
from parser import MyParser
from generatorA import CodeGenerator
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python kompilator.py <input.imp> <output.mr>")
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        with open(input_file, "r") as f:
            text = f.read()
    except:
        print(f"Cannot open input file {input_file}")
        return

    lexer = MyLexer()
    parser = MyParser()

    # --- lex + parse ---
    parse_result = parser.parse(lexer.tokenize(text))
    if parse_result is None:
        print("Parser nie zwrócił AST (błąd składni?).")
        return

    # --- generate code ---
    generator = CodeGenerator(parse_result)
    code_lines = generator.generate_code()

    try:
        with open(output_file, "w") as f:
            for line in code_lines:
                f.write(line + "\n")
    except:
        print(f"Cannot write output file {output_file}")
        return

    print("Compilation finished.")

if __name__ == "__main__":
    main()
