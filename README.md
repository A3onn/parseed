# Parseed

Parseed is a project made of a language and a transpiler that enables you to easily create parsers in any language.

The language is inspired by the C language, it is composed of structures and bitfields.


# How to use Parseed ?

## Requirements

The transpiler is written in Python 3 and uses typing annotations, so you will need Python 3.5 or greater.

No external libraries are needed.

# How to use

The transpiler can be used in the command line.

Here is an example:

```bash
./parseed.py -G python_class example/arp.py
```

# TODO

- Finish the Python generator
- Add a C generator
- Add more examples:
    - ELF
    - GIF