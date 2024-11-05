# Copyright (c) 2024 Alex Harding (alexharding.ooo)
# This file is part of PySequitur which is released under MIT license.
# See file LICENSE for full license details.

"""
PySequitur - A tool for parsing and manipulating file sequences.

This package provides tools for working with frame-based file sequences,
commonly used in VFX and animation pipelines.

Classes:
    FileSequence: Manages collections of related files as a sequence
    Parser: Utility class for parsing filenames and discovering sequences
    Components: Configuration class for specifying filename components
"""

from typing import List, Type

__version__ = "0.1.0"

from .file_sequence import (  # type: ignore
    Item,
    FileSequence,
    Parser,
    Components,
)

# Type definitions for better IDE support
ItemType = Type[Item]
FileSequenceType = Type[FileSequence]
ParserType = Type[Parser]
ComponentsType = Type[Components]

__all__: List[str] = [
    "Item",
    "FileSequence",
    "Parser",
    "Components",
]
