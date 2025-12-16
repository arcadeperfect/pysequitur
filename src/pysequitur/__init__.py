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

# from typing import List, type

__version__ = "0.1.1"

# from .crawl import Node, visualize_tree
from . import crawl
from .file_sequence import (
    Components,
    ExecutionResult,
    FileSequence,
    Item,
    ItemParser,
    OperationPlan,
    SequenceBuilder,
    SequenceFactory,
    SequenceParser,
    SequenceResult,
    ItemResult,
)
from .file_types import MOVIE_FILE_TYPES

# from . import integrations  # Add this line

# Type definitions for better IDE support
ItemType = type[Item]
FileSequenceType = type[FileSequence]
ComponentsType = type[Components]

__all__: list[str] = [
    "Item",
    "FileSequence",
    "Components",
    "ItemParser",
    "SequenceParser",
    "crawl",
    "SequenceFactory",
    "SequenceBuilder",
    "SequenceResult",
    "ItemResult",
    "OperationPlan",
    "ExecutionResult",
    "MOVIE_FILE_TYPES",
]
