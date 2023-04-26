#!/usr/bin/env python3
from lexer import Lexer, Token
from test_generator import start_test_generator
from parser import Parser
from ast_nodes import ASTNode
from transpiler import ParseedOutputGenerator, Writer
from errors import ParseedBaseError
from typing import List
from glob import glob
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from importlib import import_module
from sys import argv as sys_argv
import argparse, os

console = Console()
err_console = Console(stderr=True, style="bold red")

def main():
    # import generators dynamically
    for file_path in glob("generators" + os.path.sep + "*.py"):
        filename = os.path.basename(file_path)
        # importing "generators.<file name without '.py'>"
        import_module("generators." + Path(filename).stem)

    argparser = argparse.ArgumentParser(description="A simple language simplifying the creation of parsers.")
    argparser.add_argument("file", help="File to parse", nargs="?", default="")
    argparser.add_argument("-o", "--output", help="Output file of the generated code ('-' for STDOUT).", dest="output_file", default="-")
    argparser.add_argument("-n", "--no-color", help="Disable colors when printing to STDOUT and STDERR.", dest="no_color", action="store_true")
    argparser.add_argument("-L", "--lexer", action="store_true", help="Print the lexer's list of tokens", dest="show_lexer")
    argparser.add_argument("-A", "--ast", action="store_true", help="Print the abstract syntax tree", dest="show_ast")
    argparser.add_argument("-T", "--test-generator", help="Test a generator by generating a specific parser from the generator and its corresponding binary file to test on. \
                           The argument must be the directory where these 2 files will be generated.", dest="test_generator", default=None, metavar="OUTPUT_DIR")
    argparser.add_argument("-g", "--generator", help="The generator to use", dest="generator",
                            choices=[c.__name__ for c in ParseedOutputGenerator.__subclasses__()], default=ParseedOutputGenerator.__subclasses__()[0].__name__)

    arguments = argparser.parse_args()

    # reference of the generator's class
    generator_class = next(filter(lambda cls: cls.__name__ == arguments.generator, ParseedOutputGenerator.__subclasses__()))

    if arguments.no_color:
        console.no_color = True
        err_console.no_color = True

    if arguments.test_generator != None:
        if arguments.output_file == "-":
            err_console.print(f"{sys_argv[0]}: Cannot output to STDOUT ('-') when testing a generator, please choose an output name with the '--output' parameter.")
            return 1

        try:
            return start_test_generator(generator_class, arguments.test_generator, arguments.output_file)
        except OSError as e:
            err_console.print(f"{sys_argv[0]}: {str(e)}")
            return 1
        except ParseedBaseError as e:
            err_console.print(f"{sys_argv[0]}: {str(e)}")
            return 1

    if arguments.file == "":
        console.print(f"Using generator: [italic bold]{generator_class.__name__}[/italic bold]")
        while True:
            try:
                lexer = Lexer(console.input("Parseed [blue]>[/blue] "), "<stdin>")
            except EOFError:
                err_console.print("[green]Quitting...[/green]")
                break
            except KeyboardInterrupt:
                err_console.print("[green]Quitting...[/green]")
                break
            run(lexer, arguments, generator_class)
    else:
        try:
            with open(arguments.file, "r") as f:
                lexer = Lexer(f.read(), arguments.file)
                run(lexer, arguments, generator_class)
        except OSError as e:
            err_console.print(f"[red]{sys_argv[0]}:[/red] {str(e)}")
            return 1


def run(lexer, arguments, generator_class):
    try:
        tokens = lexer.run()
    except ParseedBaseError as e:
        err_console.print(e)  # just print the error
        return

    if arguments.show_lexer:
        lexer_pprint(tokens)

    parser = Parser(tokens)
    try:
        ast = parser.run()
    except ParseedBaseError as e:
        err_console.print(e)  # just print the error
        return
    if arguments.show_ast:
        AST_pprint(ast)

    writer: Writer = Writer()
    try:
        generator_class(ast).generate(writer)
    except ParseedBaseError as e:
        err_console.print(e)  # just print the error
        return

    if arguments.output_file == "-":
        console.print(Syntax(writer.generate_code(), generator_class.PYGMENT_HIGHLIGHTER))
    else:
        try:
            with open(arguments.output_file, "w") as f:
                f.write(writer.generate_code())
        except OSError as e:
            err_console.print(e)


def AST_pprint(ast: List[ASTNode]) -> str:
    res: str = ""
    if ast is None:
        res = "<Empty>"
    else:
        res = "\n".join([node.to_str() for node in ast])

    console.print(Panel(res, title="AST"))
    console.print("") # empty line


def lexer_pprint(tokens: List[Token]):
    res: str = ""
    if tokens is None:
        res = "<Empty>"
    else:
        last_token: Token = tokens[0]
        res = f"({last_token.type}:{last_token.value} "
        for token in tokens[1:]:
            if last_token.pos_start.ln != token.pos_start.ln:
                res += "\n" + (" " * token.pos_start.col)

            if token.value is not None:
                res += f"({token.type}:{token.value}) "
            else:
                res += f"{token.type} "
            last_token = token
    console.print(Panel(res, title="Lexer"))
    console.print("") # empty line


if __name__ == "__main__":
    main()
