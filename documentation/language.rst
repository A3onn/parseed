****************************
Parseed's language reference
****************************

.. contents:: Table of contents
    :local:


Parseed possess its own language inspired by C.

This language is meant to be easy to write and to read.

Anybody with some experience with C can easily learn this language.


Each "program" is composed of structures and bitfields.

Structures are like C's :code:`struct`, but in parseed they can have more informations along them.

Structures
==========

.. code-block:: Bnf

    <struct_stmt> ::= <endian>+ "struct" <identifier> "{" (<struct_member_def> | <match_stmt>)+ "}"


Structures are one of the principal parts of the language.

They are made of members and can have some logic with `Match Statement`_ that let you control which type or member to use based on a condition.


Members
*******

.. code-block:: Bnf

    <struct_member_def> ::= <struct_member_type> <identifier> ","

    <struct_member_type> ::= (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>)
                            | (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>) "[" <expr> "]"
                            | (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>) "[]"


Data type
---------

.. code-block:: Bnf

    <data_type> ::= "uint8" | "int8" | "uint16" | "int16" | "uint24" | "int24" | "uint32" | "int32" | "uint40" | "int40" | "uint48" | "int48" | "uint64" | "int64" | "uint128" | "int128" | "float" | "double" | <string_data_type>

    <ternary_data_type> ::= "(" <comparison> "?" (<data_type>|<identifier>) ":" (<data_type>|<identifier>) ")"


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


String
^^^^^^

.. code-block:: Bnf

    <string_data_type> ::= "string" ( '(' (<expr> | <string> | <char>) ')' )?


Endianness
----------

.. code-block:: Bnf

    <endian> ::= "LE" | "BE"

    <ternary_endian> ::= "(" <comparison> "?" <endian> ":" <endian> ")"


List
----

.. code-block:: Bnf

    (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>) "[" <expr> "]"
    (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>) "[]"  ;; repeat this member until the end of the buffer


Declared length
^^^^^^^^^^^^^^^

.. code-block:: Bnf

    (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>) "[" <expr> "]"


Un-declared length
^^^^^^^^^^^^^^^^^^

.. code-block:: Bnf

    (<endian> | <ternary_endian>)+ (<data_type> | <ternary_data_type> | <identifier>) "[]"  ;; repeat this member until the end of the buffer


Match statement
***************

.. code-block:: Bnf

    <match_stmt> ::= "match (" <expr> ") {" (<expr> ":" <struct_member_type> ",")+ "}" <identifier> ","
                    | "match (" <expr> ") {" (<expr> ": {" <struct_member_def>+ "},")+ "},"


Bitfields
=========

.. code-block:: Bnf

    <bitfield_stmt> ::= "bitfield" <identifier> "{" <bitfield_member_def>+ "}"
                        | "bitfield" <identifier> "(" <no_identifier_expr> ")" "{" <bitfield_member_def>+ "}"

Bitfields are a pack of bytes where each bit (or multiple at once) represent a value.

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

Bitfield's length
*****************

.. code-block:: Bnf

    "bitfield" <identifier> "(" <no_identifier_expr> ")" "{" <bitfield_member_def>+ "}"


Member's length
***************

.. code-block:: Bnf

    <bitfield_member_def> ::= <identifier> "(" <no_identifier_expr> ")"? ","
