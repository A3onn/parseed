****************************
Parseed's language reference
****************************

.. contents:: Table of contents
    :local:


Structures
==========

Members
*******

Data type
---------

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

Endianness
----------

List
----

Declared length
^^^^^^^^^^^^^^^

Un-declared length
^^^^^^^^^^^^^^^^^^

Match statement
***************

Bitfields
=========

Bitfield's length
*****************

Member's length
***************