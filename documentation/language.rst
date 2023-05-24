****************************
Parseed's language reference
****************************

.. contents:: Table of contents
    :local:


Parseed possess its own language inspired by C.

This language is meant to be easy to write and to read.

Anybody with some experience with C can easily learn and use this language.


Each "program" is composed of structs and bitfields.

Structures are like C's :code:`struct`, the difference is that they can have some logic in them throught the use of ternary operators and match statements.

Structures
==========

.. code-block:: Bnf

    <struct_stmt> ::= <endian>+ "struct" <identifier> "{" (<struct_member_def> | <match_stmt>)+ "}"


Structures are one of the principal parts of the language.

They are made of members that will be populated when parsing a blob (ex: a file).


Members
*******

.. code-block:: Bnf

    <struct_member_def> ::= <struct_member_type> <identifier> ","

    <struct_member_type> ::= (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>)
                            | (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>) "[" <expr> "]"
                            | (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>) "[]"

Just like C's :code:`struct`, a member has a type that can be a basic data-type or another struct.

Data type
---------

.. code-block:: Bnf

    <data_type> ::= <string_data_type> | <bytes_data_type> | "uint8" | "int8" | "uint16" | "int16" | "uint24" | "int24" | "uint32" | "int32" | "uint40" | "int40" | "uint48" | "int48" | "uint64" | "int64" | "uint128" | "int128" | "float" | "double"

    <ternary_data_type> ::= "(" <comparison> "?" (<data_type>|<identifier>) ":" (<data_type>|<identifier>) ")"

Data-types are basic types that have a size, endianness and a sign for integers.

Here is the table of data-types available and some informations about each one:

.. csv-table:: Data types information table
    :header: "Name", "Size", "Signed", "Description"
    :delim: ;
    :widths: auto

    uint8; 1; no; --
    int8; 1; yes; --
    uint16; 2; no; --
    int16; 2; yes; --
    uint24; 3; no; --
    int24; 3; yes; --
    uint32; 4; no; --
    int32; 4; yes; --
    uint40; 5; no; --
    int40; 5; yes; --
    uint48; 6; no; --
    int48; 6; yes; --
    uint64; 8; no; --
    int64; 8; yes; --
    uint128; 16; no; --
    int128; 16; yes; --
    float; 4; no; IEEE754
    double; 8; no; IEEE754 (binary64)
    string; "variable"; no; Strings ends with a '\\0' by default, otherwise it is precised in parenthesis after.
    bytes; "variable"; no; Bytes ends with a '\\0' by default, otherwise it is precised in parenthesis after.


String
^^^^^^

.. code-block:: Bnf

    <string_data_type> ::= "string" ( '(' (<num_int> | <string> | <char> | <identifier>) ')' )?

A string is is list of characters ending with a delimiter.

By default the delimiter is a null-byte, but it can either be a single character, a string or an integer (useful for non-printable characters).

It can also be an expression, in this case the resulting value should be an integer.

If the deimiter is an identifier, its data-type should either be string or a integer (the size does not matter, if , must be printable).

Notes:
The the delimiter will be consumed when parsing but won't be present in the member's value.

Every byte making the string should be printable, otherwise you should use the Bytes data-type.

Bytes
-----

.. code-block:: Bnf

    <bytes_data_type> ::= "bytes(" (<num_int> | <string> | <char> | <identifier>) ")" ;; "bytes(delimitor)"

The bytes data-type is a list of bytes ending with a delimiter.

Like the string data-type, the delimiter is consumed in the parser but not included.

Bytes are meant to be used when the size of the content is delimited, if you don't have a delimiter but you know the size, you can use a list.

Endianness
----------

.. code-block:: Bnf

    <endian> ::= "LE" | "BE"

    <ternary_endian> ::= "(" <comparison> "?" <endian> ":" <endian> ")"


It is possible to specify the endianness of a single member or for a struct.

By default everything is in big endian.

If you specify the endianness for a member with a struct as data-type, it will take over the struct's default endianness.

List
----

.. code-block:: Bnf

    (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>) "[" <expr> "]"
    (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>) "[]"  ;; repeat this member until the end of the buffer


Lists are a number on contiguous values with the same type.

It is possible to omit the size of the list, in this case the parser will try to parse as much as it can before continuing to parse the following members and structs.
You cannot use this possibility twice in the struct or sub-struct, for exemple:

This is correct:

.. code-block::

    struct Some_struct {
        uint8 some_member,
        float[] some_unknown_size_member,
        int16 final_member,
    }

And so it is:

.. code-block::

    struct Footer {
        uint16 flags,
        float[] some_unknown_size_member,
    }

    struct Some_struct {
        uint8 some_member,
        Footer footer,
    }

This is incorrect:

.. code-block::

    struct Some_struct {
        int128 some_member,
        float[] some_unknown_size_member,
        uint16 another_member,
        double[] another_unknown_size_member,
    }

.. code-block::

    struct Footer {
        uint64 flags,
        float[] another_unknown_size_member_in_a_substruct,
    }

    struct Some_struct {
        int48 some_member,
        int32[] some_unknown_size_member,
        Footer footer,
    }


Match statement
***************

.. code-block:: Bnf

    <match_stmt> ::= "match (" <expr> ") {" (<expr> ":" <struct_member_type> ",")+ "}" <identifier> ","
                    | "match (" <expr> ") {" (<expr> ": {" <struct_member_def>+ "},")+ "},"

A match statement

Bitfields
=========

.. code-block:: Bnf

    <bitfield_stmt> ::= <endian>+ "bitfield" <identifier> "{" <bitfield_member_def>+ "}"
                        | <endian>+ "bitfield" <identifier> "(" <no_identifier_expr> ")" "{" <bitfield_member_def>+ "}"

Bitfields are a pack of bytes where each bit (or multiple at once) represents a flag.

This is used a lot to compress booleans in just a few bytes instead of one byte for each boolean.

Here is an exemple using TCP `flags <https://en.wikipedia.org/wiki/Transmission_Control_Protocol#TCP_segment_structure>`_:

.. code-block:: C

    bitfield TCP_flags {
        NS,
        CWR,
        ECE,
        URG,
        ACK,
        PSH,
        RST,
        SYN,
        FIN
    }

You can specify the endianness of the whole bitfield like struct, but not for individual member.

Bitfield's length
*****************

.. code-block:: Bnf

    "bitfield" <identifier> "(" <no_identifier_expr> ")" "{" <bitfield_member_def>+ "}"

Bitfields can have an arbitrary length expressed in bytes.

The default size is the sum of the sizes of its members divided by 8 and floored.


Member's length
***************

.. code-block:: Bnf

    <bitfield_member_def> ::= <identifier> "(" <no_identifier_expr> ")"? ","

A member can take any size, this size is expressed in bits and cannot have an identifier in it.
