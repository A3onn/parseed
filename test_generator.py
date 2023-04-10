#!/usr/bin/env python3
from errors import ParseedBaseError
from transpiler import ParseedOutputGenerator, Writer
from lexer import Lexer
from parser import Parser
import os, struct

PARSER_CODE = """
struct Unsigned_Numbers {
    uint8 one,
    uint16 two,
    uint24 three,
    uint32 four,
    uint40 five,
    uint48 six,
    uint64 seven,
    uint128 height,
}

struct Signed_Numbers {
    int8 minus_one,
    int16 minus_two,
    int24 minus_three,
    int32 minus_four,
    int40 minus_five,
    int48 minus_six,
    int64 minus_seven,
    int128 minus_height,
}

BE struct Big_Endian {
    Unsigned_Numbers unsigned_numbers,
    Signed_Numbers signed_numbers,
}

LE struct Little_Endian {
    Unsigned_Numbers unsigned_numbers,
    Signed_Numbers signed_numbers,
}

struct Root_Struct {
    Big_Endian big_endian,
    Little_Endian little_endian,
}
"""

def start_test_generator(generator_class: ParseedOutputGenerator, output_dir: str, output_name: str) -> int:
    lexer = Lexer(PARSER_CODE, "-")
    parser = Parser(lexer.run())
    ast = parser.run()

    writer = Writer()

    try:
        generator_class(ast).generate(writer)
    except ParseedBaseError as e:
        print(e)  # just print the error
        return 1

    with open(output_dir + os.sep + output_name, "w") as f:
        f.write(writer.generate_code())
    
    generate_binary_test_file(output_dir)


def generate_binary_test_file(output_dir: str):
    with open(output_dir + os.sep + "binary_test_file.bin", "wb") as f:
        # BE struct Big_Endian

        # struct Unsigned_Numbers
        for i in range(7):
            f.write((i).to_bytes(i, byteorder="big", signed=False))

        f.write((7).to_bytes(8, byteorder="big", signed=False))
        f.write((8).to_bytes(16, byteorder="big", signed=False))

        # struct Signed_Numbers
        for i in range(7):
            f.write((-i).to_bytes(i, byteorder="big", signed=True))

        f.write((-7).to_bytes(8, byteorder="big", signed=True))
        f.write((-8).to_bytes(16, byteorder="big", signed=True))
        

        # BE struct Big_Endian

        # struct Unsigned_Numbers
        for i in range(7):
            f.write((i).to_bytes(i, byteorder="little", signed=False))

        f.write((7).to_bytes(8, byteorder="little", signed=False))
        f.write((8).to_bytes(16, byteorder="little", signed=False))

        # struct Signed_Numbers
        for i in range(7):
            f.write((-i).to_bytes(i, byteorder="little", signed=True))

        f.write((-7).to_bytes(8, byteorder="little", signed=True))
        f.write((-8).to_bytes(16, byteorder="little", signed=True))