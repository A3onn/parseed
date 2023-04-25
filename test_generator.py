#!/usr/bin/env python3
from errors import ParseedBaseError
from transpiler import ParseedOutputGenerator, Writer
from lexer import Lexer
from parser import Parser
import os, struct

PARSER_CODE = """
struct Strings {
    string hello_world_null_byte,
    string('a') hello_world_a_char_terminated,
    string("test") hello_world_test_string_terminated,
    string(1) hello_world_one_terminated,
}

struct Bytes {
    bytes(0) test_zero_terminated,
    bytes(\\x15) TEST_fifteen_terminated,
}

struct Floating_Point_Numbers {
    float one_dot_one,
    double two_dot_two,
}

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
    Floating_Point_Numbers floating_point_numbers,
    Strings strings,
}

LE struct Little_Endian {
    Unsigned_Numbers unsigned_numbers,
    Signed_Numbers signed_numbers,
    Floating_Point_Numbers floating_point_numbers,
    Strings strings,
}

struct Root_Struct {
    Big_Endian big_endian,
    Little_Endian little_endian,
}
"""

def start_test_generator(generator_class: ParseedOutputGenerator, output_dir: str, output_name: str) -> int:
    # errors 
    lexer = Lexer(PARSER_CODE, "-")
    parser = Parser(lexer.run())
    ast = parser.run()

    writer = Writer()
    generator_class(ast).generate(writer)

    with open(output_dir + os.sep + output_name, "w") as f:
        f.write(writer.generate_code())
    
    generate_binary_test_file(output_dir)


def generate_binary_test_file(output_dir: str):
    with open(output_dir + os.sep + "binary_test_file.bin", "wb") as f:
        generate_numbers_binary_file(f, "big")
        generate_numbers_binary_file(f, "little")


def generate_numbers_binary_file(f, endian: str):
        # struct Unsigned_Numbers
        for i in range(7):
            f.write((i).to_bytes(i, byteorder=endian, signed=False))

        f.write((7).to_bytes(8, byteorder=endian, signed=False))
        f.write((8).to_bytes(16, byteorder=endian, signed=False))

        # struct Signed_Numbers
        for i in range(7):
            f.write((-i).to_bytes(i, byteorder=endian, signed=True))

        f.write((-7).to_bytes(8, byteorder=endian, signed=True))
        f.write((-8).to_bytes(16, byteorder=endian, signed=True))

        # struct Floating_Point_Numbers
        endian_char = "<" if endian == "little" else ">"
        f.write(struct.pack(endian_char + "f", 1.1))
        f.write(struct.pack(endian_char + "d", 2.2))

        # struct Strings
        f.write(struct.pack(endian_char + str(len("Hello world\0")) + "s", b"Hello world\0"))
        f.write(struct.pack(endian_char + str(len("Hello worlda")) + "s", b"Hello worlda"))
        f.write(struct.pack(endian_char + str(len("Hello worldtest")) + "s", b"Hello worldtest"))
        f.write(struct.pack(endian_char + str(len("Hello world\01")) + "s", b"Hello world\01"))

        # struct Bytes
        f.write(struct.pack(endian_char + str(len("test\00")) + "s", b"test\00"))
        f.write(struct.pack(endian_char + str(len("TEST\00")) + "s", b"TEST\00"))