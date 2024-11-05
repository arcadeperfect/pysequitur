# Copyright (c) 2024 Alex Harding (alexharding.ooo)
# This file is part of PySequitur which is released under MIT license.
# See file LICENSE for full license details.
"""
PySequitur - A tool for parsing and manipulating file sequences.

This package provides tools for working with frame-based file sequences,
commonly used in VFX and animation pipelines.

Classes:
    Item: Represents a single item in a file sequence
    FileSequence: Manages collections of related files as a sequence
    Components: Configuration class for specifying filename components
"""

from typing import List, Type

__version__ = "0.1.0"

from .file_sequence import Item, FileSequence, Components  # type: ignore

# Type definitions for better IDE support
ItemType = Type[Item]
FileSequenceType = Type[FileSequence]
ComponentsType = Type[Components]

__all__: List[str] = [
    "Item",
    "FileSequence",
    "Components",
]
