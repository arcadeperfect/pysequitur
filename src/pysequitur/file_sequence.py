# Copyright (c) 2024 Alex Harding (alexharding.ooo)
# This file is part of PySequitur which is released under MIT license.
# See file LICENSE for full license details.

from __future__ import annotations

import dataclasses
import importlib.util
import logging
import os
import re
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum, Flag, auto
from operator import attrgetter
from pathlib import Path
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    TypedDict,
    Union,
)

logger = logging.getLogger("pysequitur")
logger.addHandler(logging.NullHandler())


# =============================================================================
# Operation Infrastructure
# =============================================================================


class OperationType(Enum):
    """Types of filesystem operations."""

    RENAME = auto()
    MOVE = auto()
    COPY = auto()
    DELETE = auto()


@dataclass(frozen=True)
class FileOperation:
    """An immutable description of a single file operation.

    Attributes:
        operation: The type of operation (RENAME, MOVE, COPY, DELETE)
        source: The source file path
        destination: The destination file path (None for DELETE operations)
    """

    operation: OperationType
    source: Path
    destination: Optional[Path]

    @property
    def would_overwrite(self) -> bool:
        """Check if destination already exists."""
        return self.destination is not None and self.destination.exists()

    def execute(self) -> None:
        """Actually perform the operation on the filesystem."""
        if self.operation == OperationType.RENAME:
            if self.destination is None:
                raise ValueError("Rename requires destination")
            self.source.rename(self.destination)
        elif self.operation == OperationType.MOVE:
            if self.destination is None:
                raise ValueError("Move requires destination")
            shutil.move(str(self.source), str(self.destination))
        elif self.operation == OperationType.COPY:
            if self.destination is None:
                raise ValueError("Copy requires destination")
            shutil.copy2(self.source, self.destination)
        elif self.operation == OperationType.DELETE:
            self.source.unlink()
        else:
            raise ValueError(f"Unknown operation: {self.operation}")

    def __repr__(self) -> str:
        op_name = self.operation.name
        if self.operation == OperationType.DELETE:
            return f"FileOperation({op_name}: {self.source})"
        return f"FileOperation({op_name}: {self.source} -> {self.destination})"


@dataclass(frozen=True)
class ExecutionResult:
    """Result of executing an OperationPlan."""

    executed: Tuple[FileOperation, ...]
    failed: Tuple[Tuple[FileOperation, Exception], ...] = ()  # noqa: E501

    @property
    def success(self) -> bool:
        """Returns True if all operations succeeded."""
        return len(self.failed) == 0

    @property
    def count(self) -> int:
        """Returns total number of executed operations."""
        return len(self.executed)


@dataclass(frozen=True)
class OperationPlan:
    """A batch of operations that can be previewed and executed.

    OperationPlan represents a set of filesystem operations that have been
    planned but not yet executed. This allows inspection of what will happen
    before committing to the changes.

    Example:
        new_item, plan = item.rename(Components(prefix="new"))
        print(plan)  # See what will happen
        if not plan.has_conflicts:
            result = plan.execute()
    """

    operations: Tuple[FileOperation, ...]

    @property
    def conflicts(self) -> List[FileOperation]:
        """Operations that would overwrite existing files."""
        return [op for op in self.operations if op.would_overwrite]

    @property
    def has_conflicts(self) -> bool:
        """Returns True if any operation would overwrite an existing file."""
        return len(self.conflicts) > 0

    @property
    def sources(self) -> List[Path]:
        """List of all source paths in this plan."""
        return [op.source for op in self.operations]

    @property
    def destinations(self) -> List[Path]:
        """List of all destination paths in this plan."""
        return [op.destination for op in self.operations if op.destination is not None]

    def execute(self, *, force: bool = False) -> ExecutionResult:
        """
        Execute all operations in the plan.

        Args:
            force: If True, overwrite existing files. If False, raise on conflict.

        Returns:
            ExecutionResult with success/failure details.

        Raises:
            FileExistsError: If conflicts exist and force=False.
        """
        if self.has_conflicts and not force:
            conflict_paths = [op.destination for op in self.conflicts]
            raise FileExistsError(f"Conflicts detected: {conflict_paths}")

        executed: List[FileOperation] = []
        failed: List[Tuple[FileOperation, Exception]] = []

        for op in self.operations:
            try:
                op.execute()
                executed.append(op)
            except Exception as e:
                failed.append((op, e))

        return ExecutionResult(executed=tuple(executed), failed=tuple(failed))

    @classmethod
    def empty(cls) -> OperationPlan:
        """Return an empty plan (no-op)."""
        return cls(operations=())

    def __add__(self, other: OperationPlan) -> OperationPlan:
        """Combine two plans into one."""
        return OperationPlan(operations=self.operations + other.operations)

    def __repr__(self) -> str:
        if not self.operations:
            return "OperationPlan(empty)"
        lines = [f"OperationPlan ({len(self.operations)} operations):"]
        for op in self.operations[:10]:
            if op.operation == OperationType.DELETE:
                lines.append(f"  {op.operation.name}: {op.source}")
            else:
                lines.append(f"  {op.operation.name}: {op.source} -> {op.destination}")
        if len(self.operations) > 10:
            lines.append(f"  ... and {len(self.operations) - 10} more")
        if self.has_conflicts:
            lines.append(f"  WARNING: {len(self.conflicts)} conflicts detected")
        return "\n".join(lines)


# =============================================================================
# Result Types - Named tuples with .apply() convenience
# =============================================================================


@dataclass(frozen=True)
class ItemResult:
    """Result of an Item operation containing the proposed new state and plan.

    Provides a convenient `.apply()` method to execute the plan and return
    the new Item in one call.

    Attributes:
        item: The proposed new Item state
        plan: The OperationPlan to execute

    Example:
        # Traditional usage
        result = item.rename(Components(prefix="new"))
        result.plan.execute()
        new_item = result.item

        # Convenient usage
        new_item = item.rename(Components(prefix="new")).apply()
    """

    item: Item
    plan: OperationPlan

    def apply(self, *, force: bool = False) -> Item:
        """Execute the plan and return the new Item.

        Args:
            force: If True, overwrite existing files on conflict.

        Returns:
            The new Item after execution.

        Raises:
            FileExistsError: If conflicts exist and force=False.
        """
        self.plan.execute(force=force)
        return self.item

    def __iter__(self) -> Iterator:
        """Allow tuple unpacking: item, plan = result"""
        return iter((self.item, self.plan))


@dataclass(frozen=True)
class SequenceResult:
    """Result of a FileSequence operation containing proposed new state and plan.

    Provides a convenient `.apply()` method to execute the plan and return
    the new FileSequence in one call.

    Attributes:
        sequence: The proposed new FileSequence state
        plan: The OperationPlan to execute

    Example:
        # Traditional usage
        result = sequence.rename(Components(prefix="new"))
        result.plan.execute()
        new_seq = result.sequence

        # Convenient usage
        new_seq = sequence.rename(Components(prefix="new")).apply()
    """

    sequence: FileSequence
    plan: OperationPlan

    def apply(self, *, force: bool = False) -> FileSequence:
        """Execute the plan and return the new FileSequence.

        Args:
            force: If True, overwrite existing files on conflict.

        Returns:
            The new FileSequence after execution.

        Raises:
            FileExistsError: If conflicts exist and force=False.
        """
        self.plan.execute(force=force)
        return self.sequence

    def __iter__(self) -> Iterator:
        """Allow tuple unpacking: sequence, plan = result"""
        return iter((self.sequence, self.plan))


# =============================================================================
# Core Data Types
# =============================================================================


class SequenceExistence(Enum):
    FALSE = auto()
    PARTIAL = auto()
    TRUE = auto()


@dataclass(frozen=True)
class Components:
    """Configuration class for naming operations on Items and FileSequences.

    Provides a flexible way to specify components of a filename during renaming
    or parsing operations. Components is immutable (frozen).

    Any component left as None will retain its original value when merged.

    Attributes:
        prefix (str, optional): New base name
        delimiter (str, optional): New delimiter between name and frame number
        padding (int, optional): New frame number padding length
        suffix (str, optional): New suffix after frame number
        extension (str, optional): New file extension
        frame_number (int, optional): New frame number

    Example:
        Components(prefix="new_name", padding=4) when applied would change:
        "old_001.exr" to "new_name_0001.exr"

    """

    prefix: Optional[str] = None
    delimiter: Optional[str] = None
    padding: Optional[int] = None
    suffix: Optional[str] = None
    extension: Optional[str] = None
    frame_number: Optional[int] = None

    def with_frame_number(self, frame_number: int) -> Components:
        """Return a new Components with the given frame number.

        Adjusts padding if necessary to accommodate the frame number.
        """
        new_padding = self.padding
        if new_padding is not None:
            new_padding = max(new_padding, len(str(frame_number)))
        else:
            new_padding = len(str(frame_number))

        return Components(
            prefix=self.prefix,
            delimiter=self.delimiter,
            padding=new_padding,
            suffix=self.suffix,
            extension=self.extension,
            frame_number=frame_number,
        )

    def merge_with_defaults(
        self,
        prefix: str,
        delimiter: Optional[str],
        padding: int,
        suffix: Optional[str],
        extension: str,
        frame_number: int,
    ) -> Components:
        """Return a new Components with None values filled from defaults.

        This is a pure function that doesn't mutate self.
        """
        return Components(
            prefix=self.prefix if self.prefix is not None else prefix,
            delimiter=self.delimiter if self.delimiter is not None else delimiter,
            padding=self.padding if self.padding is not None else padding,
            suffix=self.suffix if self.suffix is not None else suffix,
            extension=self.extension if self.extension is not None else extension,
            frame_number=(
                self.frame_number if self.frame_number is not None else frame_number
            ),
        )

    # -------------------------------------------------------------------------
    # Builder pattern methods for fluent API
    # -------------------------------------------------------------------------

    def with_prefix(self, prefix: str) -> Components:
        """Return a new Components with the given prefix."""
        return dataclasses.replace(self, prefix=prefix)

    def with_delimiter(self, delimiter: str) -> Components:
        """Return a new Components with the given delimiter."""
        return dataclasses.replace(self, delimiter=delimiter)

    def with_padding(self, padding: int) -> Components:
        """Return a new Components with the given padding."""
        return dataclasses.replace(self, padding=padding)

    def with_suffix(self, suffix: str) -> Components:
        """Return a new Components with the given suffix."""
        return dataclasses.replace(self, suffix=suffix)

    def with_extension(self, extension: str) -> Components:
        """Return a new Components with the given extension."""
        return dataclasses.replace(self, extension=extension)

    @classmethod
    def build(
        cls,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        padding: Optional[int] = None,
        suffix: Optional[str] = None,
        extension: Optional[str] = None,
    ) -> Components:
        """Factory method to create Components with a fluent API.

        Example:
            Components.build().with_prefix("new").with_extension("exr")
        """
        return cls(
            prefix=prefix,
            delimiter=delimiter,
            padding=padding,
            suffix=suffix,
            extension=extension,
        )


def _validate_suffix(suffix: Optional[str]) -> None:
    """Validate that suffix contains no digits."""
    if suffix is not None and any(char.isdigit() for char in suffix):
        raise ValueError("suffix cannot contain digits")


@dataclass(frozen=True)
class Item:
    """Represents a single file in an image sequence.

    Item is immutable (frozen). All operations that would modify an Item
    return a tuple of (new_item, operation_plan) where new_item is the
    proposed new state and operation_plan contains the filesystem operations
    needed to realize that state.

    Attributes:
        prefix: The base name of the file
        frame_string: The frame number as a string (preserves padding)
        extension: The file extension
        delimiter: Optional delimiter between prefix and frame
        suffix: Optional suffix after frame number
        directory: Optional directory path
    """

    prefix: str
    frame_string: str
    extension: str
    delimiter: Optional[str] = None
    suffix: Optional[str] = None
    directory: Optional[Path] = None

    def __post_init__(self) -> None:
        _validate_suffix(self.suffix)

    @staticmethod
    def from_path(path: Path) -> Optional[Item]:
        """Creates an Item object from a Path object.

        Args:
            path: Path object representing the file
        """
        if not path.name:
            raise ValueError("Path object must have a name")
        return ItemParser.item_from_filename(path.name, path.parent)

    @staticmethod
    def from_file_name(
        file_name: str, directory: Optional[Path] = None
    ) -> Optional[Item]:
        """Creates an Item object from a filename string."""
        return ItemParser.item_from_filename(file_name, directory)

    @staticmethod
    def from_components(
        components: Components, frame: int, directory: Optional[Path] = None
    ) -> Item:
        """Creates an Item object from Components and a frame number."""
        return ItemParser.item_from_components(components, frame, directory)

    @property
    def path(self) -> Path:
        """Returns the path of the item."""
        return self.absolute_path

    @property
    def filename(self) -> str:
        """Returns the filename of the item as a string."""
        s = self.delimiter if self.delimiter else ""
        p = self.suffix if self.suffix else ""
        e = f".{self.extension}" if self.extension else ""
        return f"{self.prefix}{s}{self.frame_string}{p}{e}"

    @property
    def absolute_path(self) -> Path:
        """Returns the absolute path of the item as a Path object."""
        if self.directory is None:
            return Path(self.filename)
        return Path(self.directory) / self.filename

    @property
    def padding(self) -> int:
        """Returns the padding of the frame number as an integer."""
        return len(self.frame_string)

    @property
    def stem(self) -> str:
        """Returns the stem of the item as a string."""
        return self.path.stem

    @property
    def frame_number(self) -> int:
        """Returns the frame number as an integer."""
        return int(self.frame_string)

    @property
    def exists(self) -> bool:
        """Checks if the item exists on the filesystem."""
        return self.path.exists()

    @property
    def _min_padding(self) -> int:
        """Computes the minimum padding required to represent the frame number."""
        return len(str(int(self.frame_string)))

    # -------------------------------------------------------------------------
    # Operations - all return ItemResult (supports tuple unpacking and .apply())
    # -------------------------------------------------------------------------

    def rename(self, new_name: Components) -> ItemResult:
        """Prepare a rename operation.

        Args:
            new_name: Components specifying the new name. None values are
                     filled from current item values.

        Returns:
            ItemResult containing (new_item, plan). Supports tuple unpacking
            or use .apply() for convenience.

        Example:
            # Tuple unpacking
            new_item, plan = item.rename(Components(prefix="new"))
            plan.execute()

            # Fluent API
            new_item = item.rename(Components(prefix="new")).apply()

            # Builder pattern
            new_item = item.rename(Components.build().with_prefix("new")).apply()
        """
        if isinstance(new_name, str):
            raise TypeError("new_name must be a Components object, not a string")

        new_item = self._with_components(new_name)

        # No filesystem change needed if paths are identical
        if new_item.absolute_path == self.absolute_path:
            return ItemResult(new_item, OperationPlan.empty())

        operation = FileOperation(
            operation=OperationType.RENAME,
            source=self.absolute_path,
            destination=new_item.absolute_path,
        )

        return ItemResult(new_item, OperationPlan(operations=(operation,)))

    def move(self, new_directory: Path, create_directory: bool = False) -> ItemResult:
        """Prepare a move operation.

        Args:
            new_directory: The target directory
            create_directory: If True, create the directory if it doesn't exist

        Returns:
            ItemResult containing (new_item, plan)
        """
        logger.debug("Preparing move of %s to %s", self.filename, new_directory)

        new_item = dataclasses.replace(self, directory=new_directory)

        # No filesystem change needed if paths are identical
        if new_item.absolute_path == self.absolute_path:
            return ItemResult(new_item, OperationPlan.empty())

        # Create directory if requested (this is a side effect, happens immediately)
        if create_directory and not new_directory.exists():
            new_directory.mkdir(parents=True, exist_ok=True)

        operation = FileOperation(
            operation=OperationType.MOVE,
            source=self.absolute_path,
            destination=new_item.absolute_path,
        )

        return ItemResult(new_item, OperationPlan(operations=(operation,)))

    def copy(
        self,
        new_name: Optional[Components] = None,
        new_directory: Optional[Path] = None,
    ) -> ItemResult:
        """Prepare a copy operation.

        Args:
            new_name: Optional Components for the new name
            new_directory: Optional new directory for the copy

        Returns:
            ItemResult containing (new_item, plan)
        """
        if isinstance(new_name, str):
            raise TypeError("new_name must be a Components object")

        target_dir = new_directory if new_directory is not None else self.directory

        if new_name is not None:
            new_item = self._with_components(new_name)
            new_item = dataclasses.replace(new_item, directory=target_dir)
        else:
            new_item = dataclasses.replace(self, directory=target_dir)

        # Avoid copying to self - add "_copy" suffix
        if new_item.absolute_path == self.absolute_path:
            new_item = dataclasses.replace(new_item, prefix=self.prefix + "_copy")

        operation = FileOperation(
            operation=OperationType.COPY,
            source=self.absolute_path,
            destination=new_item.absolute_path,
        )

        return ItemResult(new_item, OperationPlan(operations=(operation,)))

    def delete(self) -> OperationPlan:
        """Prepare a delete operation.

        Returns:
            OperationPlan containing the delete operation
        """
        logger.debug("Preparing delete of %s", self.filename)

        operation = FileOperation(
            operation=OperationType.DELETE,
            source=self.absolute_path,
            destination=None,
        )

        return OperationPlan(operations=(operation,))

    def with_frame_number(
        self, new_frame_number: int, padding: Optional[int] = None
    ) -> ItemResult:
        """Prepare an operation to change the frame number.

        Args:
            new_frame_number: The new frame number
            padding: Optional new padding (defaults to current or minimum required)

        Returns:
            ItemResult containing (new_item, plan)

        Raises:
            ValueError: If new_frame_number is negative
        """
        if new_frame_number < 0:
            raise ValueError("new_frame_number cannot be negative")

        if padding is None:
            padding = self.padding

        new_padding = max(padding, len(str(new_frame_number)))
        new_frame_string = f"{new_frame_number:0{new_padding}d}"

        new_item = dataclasses.replace(self, frame_string=new_frame_string)

        # No filesystem change needed if paths are identical
        if new_item.absolute_path == self.absolute_path:
            return ItemResult(new_item, OperationPlan.empty())

        operation = FileOperation(
            operation=OperationType.RENAME,
            source=self.absolute_path,
            destination=new_item.absolute_path,
        )

        return ItemResult(new_item, OperationPlan(operations=(operation,)))

    def with_padding(self, padding: int) -> ItemResult:
        """Prepare an operation to change the padding.

        Args:
            padding: The new padding (minimum is determined by frame number)

        Returns:
            ItemResult containing (new_item, plan)
        """
        actual_padding = max(padding, len(str(self.frame_number)))
        new_frame_string = f"{self.frame_number:0{actual_padding}d}"

        new_item = dataclasses.replace(self, frame_string=new_frame_string)

        # No filesystem change needed if paths are identical
        if new_item.absolute_path == self.absolute_path:
            return ItemResult(new_item, OperationPlan.empty())

        operation = FileOperation(
            operation=OperationType.RENAME,
            source=self.absolute_path,
            destination=new_item.absolute_path,
        )

        return ItemResult(new_item, OperationPlan(operations=(operation,)))

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _with_components(self, components: Components) -> Item:
        """Return a new Item with components applied (pure, no side effects)."""
        filled = components.merge_with_defaults(
            prefix=self.prefix,
            delimiter=self.delimiter,
            padding=self.padding,
            suffix=self.suffix,
            extension=self.extension,
            frame_number=self.frame_number,
        )

        new_padding = max(filled.padding or 1, len(str(filled.frame_number or 0)))
        new_frame_string = f"{filled.frame_number:0{new_padding}d}"

        return Item(
            prefix=filled.prefix or "",
            frame_string=new_frame_string,
            extension=filled.extension or "",
            delimiter=filled.delimiter,
            suffix=filled.suffix,
            directory=self.directory,
        )


@dataclass(frozen=True)
class FileSequence:
    """Manages a collection of related Items that form an image sequence.

    FileSequence is immutable (frozen). All operations return a tuple of
    (new_sequence, operation_plan) where new_sequence is the proposed new
    state and operation_plan contains the filesystem operations to execute.

    Attributes:
        items: Tuple of Item objects that make up the sequence

    Properties:
        existing_frames: List of frame numbers present in the sequence
        missing_frames: List of frame numbers missing from the sequence
        frame_count: Total number of frames including gaps
        first_frame: Lowest frame number in the sequence
        last_frame: Highest frame number in the sequence
        prefix: Common prefix shared by all items
        extension: Common file extension shared by all items
        padding: Number of digits used in frame numbers

    Example:
        A sequence might contain:
        - render_001.exr
        - render_002.exr
        - render_003.exr
    """

    items: Tuple[Item, ...]

    def __repr__(self) -> str:
        return f"{self.sequence_string} {self.first_frame}-{self.last_frame}"

    def __getitem__(self, key: Union[int, slice]) -> Union[Item, FileSequence]:
        """Access items by frame number or slice.

        Args:
            key: Either a frame number (int) or a slice of frame numbers.

        Returns:
            Item if key is int, FileSequence if key is slice.

        Raises:
            KeyError: If frame number is not in the sequence.
            TypeError: If key is not int or slice.

        Examples:
            # Get single item by frame number
            item = sequence[1001]

            # Get subsequence by frame range
            subsequence = sequence[1001:1010]  # frames 1001-1009
            subsequence = sequence[1001:1010:2]  # every 2nd frame

            # Get last 10 frames
            last_10 = sequence[-10:]
        """
        if isinstance(key, int):
            # Handle negative indexing
            if key < 0:
                # Convert to frame-based: -1 = last frame, -2 = second to last, etc.
                sorted_items = sorted(self.items, key=lambda i: i.frame_number)
                try:
                    return sorted_items[key]
                except IndexError:
                    raise KeyError(f"Frame index {key} out of range") from None

            # Positive int: treat as frame number
            for item in self.items:
                if item.frame_number == key:
                    return item
            raise KeyError(f"Frame {key} not found in sequence")

        elif isinstance(key, slice):
            return self._slice_by_frames(key)

        else:
            raise TypeError(
                f"indices must be integers or slices, not {type(key).__name__}"
            )

    def _slice_by_frames(self, key: slice) -> FileSequence:
        """Slice the sequence by frame numbers."""
        sorted_items = sorted(self.items, key=lambda i: i.frame_number)
        frame_numbers = [item.frame_number for item in sorted_items]

        # Handle None values in slice
        start = key.start
        stop = key.stop
        step = key.step or 1

        # Handle negative start/stop (index from end)
        if start is not None and start < 0:
            start = (
                frame_numbers[start]
                if abs(start) <= len(frame_numbers)
                else frame_numbers[0]
            )
        if stop is not None and stop < 0:
            stop = (
                frame_numbers[stop]
                if abs(stop) <= len(frame_numbers)
                else frame_numbers[0]
            )

        # Default start to first frame, stop to last frame + 1
        if start is None:
            start = frame_numbers[0] if frame_numbers else 0
        if stop is None:
            stop = frame_numbers[-1] + 1 if frame_numbers else 0

        # Filter items by frame range
        if step == 1:
            selected = [
                item for item in sorted_items if start <= item.frame_number < stop
            ]
        else:
            # With step, we need to select every Nth frame starting from start
            in_range = [
                item for item in sorted_items if start <= item.frame_number < stop
            ]
            selected = in_range[::step]

        return FileSequence(items=tuple(selected))

    def frames(self, start: int, end: int) -> FileSequence:
        """Return a new FileSequence containing only frames in the given range.

        This is a more explicit alternative to slice notation.

        Args:
            start: First frame number (inclusive)
            end: Last frame number (inclusive)

        Returns:
            New FileSequence with only the specified frames.

        Example:
            # Get frames 1001-1050 (inclusive)
            subsequence = sequence.frames(1001, 1050)
        """
        selected = [item for item in self.items if start <= item.frame_number <= end]
        selected.sort(key=lambda i: i.frame_number)
        return FileSequence(items=tuple(selected))

    def __len__(self) -> int:
        """Return the number of items in the sequence."""
        return len(self.items)

    def __iter__(self) -> Iterator[Item]:
        """Iterate over items in frame order."""
        return iter(sorted(self.items, key=lambda i: i.frame_number))

    def __contains__(self, frame: int) -> bool:
        """Check if a frame number is in the sequence.

        Example:
            if 1001 in sequence:
                print("Frame 1001 exists")
        """
        return any(item.frame_number == frame for item in self.items)

    @property
    def actual_frame_count(self) -> int:
        """Returns the total number of frames in the sequence."""
        return len(self.items)

    @property
    def first_frame(self) -> int:
        """Returns the lowest frame number in the sequence."""
        return min(item.frame_number for item in self.items)

    @property
    def last_frame(self) -> int:
        """Returns the highest frame number in the sequence."""
        return max(item.frame_number for item in self.items)

    @property
    def prefix(self) -> str:
        """Returns the prefix. Validates consistency across all items."""
        return str(self._validate_property_consistency(prop_name="prefix"))

    @property
    def extension(self) -> str:
        """Returns the extension. Validates consistency across all items."""
        return str(self._validate_property_consistency(prop_name="extension"))

    @property
    def delimiter(self) -> str:
        """Returns the delimiter. Validates consistency across all items."""
        return str(self._validate_property_consistency(prop_name="delimiter"))

    @property
    def suffix(self) -> Optional[str]:
        """Returns the suffix. Validates consistency across all items."""
        return str(self._validate_property_consistency(prop_name="suffix"))

    @property
    def directory(self) -> Path:
        """Returns the directory. Validates consistency across all items."""
        directory = self._validate_property_consistency(prop_name="directory")
        if not isinstance(directory, Path):
            raise TypeError(f"{self.__class__.__name__} directory must be a Path")
        return directory

    @property
    def existing_frames(self) -> List[int]:
        """Returns a list of frame numbers present in the sequence."""
        return [item.frame_number for item in self.items]

    @property
    def missing_frames(self) -> List[int]:
        """Returns frame numbers missing from the sequence range."""
        missing = sorted(
            set(range(self.first_frame, self.last_frame + 1))
            - set(self.existing_frames)
        )
        if missing:
            logger.debug("Missing frames: %s", missing)
        return missing

    @property
    def frame_count(self) -> int:
        """Returns the total frame count (including missing frames)."""
        return self.last_frame + 1 - self.first_frame

    @property
    def padding(self) -> int:
        """Returns the most common padding in the sequence."""
        if not self.items:
            raise ValueError("No items in sequence")
        padding_counts = Counter(item.padding for item in self.items)
        return padding_counts.most_common(1)[0][0]

    @property
    def sequence_string(self) -> str:
        """Returns the sequence string pattern (e.g., 'render_####.exr')."""
        padding = "#" * self.padding
        suffix = self.suffix if self.suffix is not None else ""
        return f"{self.prefix}{self.delimiter}{padding}{suffix}.{self.extension}"

    @property
    def absolute_file_name(self) -> str:
        """Returns the absolute path with sequence string pattern."""
        return os.path.join(self.directory, self.sequence_string)

    @property
    def exists(self) -> SequenceExistence:
        """Returns the existence state of the sequence on disk."""
        existing_count = sum(1 for item in self.items if item.exists)
        if existing_count == 0:
            return SequenceExistence.FALSE
        elif existing_count == len(self.items):
            return SequenceExistence.TRUE
        else:
            return SequenceExistence.PARTIAL

    @property
    def problems(self) -> Problems:
        """Returns a flag containing all detected problems."""
        problems = Problems.check_sequence(self)
        if problems is not Problems.NONE:
            logger.debug("Problems found: %s", problems)
        return problems

    # -------------------------------------------------------------------------
    # Operations - all return SequenceResult (supports tuple unpacking and .apply())
    # -------------------------------------------------------------------------

    def rename(self, new_name: Components) -> SequenceResult:
        """Prepare a rename operation for all items in the sequence.

        Args:
            new_name: Components specifying the new name

        Returns:
            SequenceResult containing (new_sequence, plan). Supports tuple
            unpacking or use .apply() for convenience.

        Example:
            # Tuple unpacking
            new_seq, plan = sequence.rename(Components(prefix="new"))
            plan.execute()

            # Fluent API
            new_seq = sequence.rename(Components(prefix="new")).apply()
        """
        if isinstance(new_name, str):
            raise ValueError("new_name must be a Components object, not a string")

        new_items: List[Item] = []
        all_operations: List[FileOperation] = []

        for item in self.items:
            item_components = new_name.with_frame_number(item.frame_number)
            result = item.rename(item_components)
            new_items.append(result.item)
            all_operations.extend(result.plan.operations)

        return SequenceResult(
            FileSequence(items=tuple(new_items)),
            OperationPlan(operations=tuple(all_operations)),
        )

    def move(
        self, new_directory: Path, create_directory: bool = False
    ) -> SequenceResult:
        """Prepare a move operation for all items in the sequence.

        Args:
            new_directory: The target directory
            create_directory: If True, create the directory if it doesn't exist

        Returns:
            SequenceResult containing (new_sequence, plan)
        """
        if new_directory == self.directory:
            return SequenceResult(self, OperationPlan.empty())

        # Create directory if requested
        if create_directory and not new_directory.exists():
            new_directory.mkdir(parents=True, exist_ok=True)

        new_items: List[Item] = []
        all_operations: List[FileOperation] = []

        for item in self.items:
            result = item.move(new_directory, create_directory=False)
            new_items.append(result.item)
            all_operations.extend(result.plan.operations)

        return SequenceResult(
            FileSequence(items=tuple(new_items)),
            OperationPlan(operations=tuple(all_operations)),
        )

    def copy(
        self,
        new_name: Optional[Components] = None,
        new_directory: Optional[Path] = None,
        create_directory: bool = False,
    ) -> SequenceResult:
        """Prepare a copy operation for all items in the sequence.

        Args:
            new_name: Optional Components for the new name
            new_directory: Optional new directory for the copies
            create_directory: If True, create the directory if it doesn't exist

        Returns:
            SequenceResult containing (new_sequence, plan)
        """
        self.validate()

        if isinstance(new_name, str):
            raise TypeError("new_name must be a Components object, not a string")

        if isinstance(new_directory, str):
            raise TypeError("new_directory must be a Path object, not a string")

        if new_directory is not None and create_directory:
            new_directory.mkdir(parents=True, exist_ok=True)

        new_items: List[Item] = []
        all_operations: List[FileOperation] = []

        for item in self.items:
            result = item.copy(new_name, new_directory)
            new_items.append(result.item)
            all_operations.extend(result.plan.operations)

        return SequenceResult(
            FileSequence(items=tuple(new_items)),
            OperationPlan(operations=tuple(all_operations)),
        )

    def delete(self) -> OperationPlan:
        """Prepare a delete operation for all items in the sequence.

        Returns:
            OperationPlan containing all delete operations
        """
        all_operations: List[FileOperation] = []

        for item in self.items:
            plan = item.delete()
            all_operations.extend(plan.operations)

        return OperationPlan(operations=tuple(all_operations))

    def offset_frames(
        self, offset: int, padding: Optional[int] = None
    ) -> SequenceResult:
        """Prepare an operation to offset all frame numbers.

        Args:
            offset: The offset to apply to all frame numbers
            padding: Optional new padding

        Returns:
            SequenceResult containing (new_sequence, plan)

        Raises:
            ValueError: If offset would result in negative frame numbers
        """
        if offset == 0:
            return SequenceResult(self, OperationPlan.empty())

        if self.first_frame + offset < 0:
            raise ValueError("offset would yield negative frame numbers")

        if padding is None:
            padding = self.padding

        padding = max(padding, len(str(self.last_frame + offset)))

        # Sort items: if offset > 0, process high frames first to avoid collisions
        sorted_items = sorted(
            self.items,
            key=attrgetter("frame_number"),
            reverse=(offset > 0),
        )

        new_items: List[Item] = []
        all_operations: List[FileOperation] = []

        for item in sorted_items:
            result = item.with_frame_number(item.frame_number + offset, padding)
            new_items.append(result.item)
            all_operations.extend(result.plan.operations)

        # Re-sort by frame number for consistent ordering
        new_items.sort(key=attrgetter("frame_number"))

        return SequenceResult(
            FileSequence(items=tuple(new_items)),
            OperationPlan(operations=tuple(all_operations)),
        )

    def with_padding(self, padding: int) -> SequenceResult:
        """Prepare an operation to change padding for all items.

        Args:
            padding: The new padding (minimum is determined by highest frame)

        Returns:
            SequenceResult containing (new_sequence, plan)
        """
        padding = max(padding, len(str(self.last_frame)))

        new_items: List[Item] = []
        all_operations: List[FileOperation] = []

        for item in self.items:
            result = item.with_padding(padding)
            new_items.append(result.item)
            all_operations.extend(result.plan.operations)

        return SequenceResult(
            FileSequence(items=tuple(new_items)),
            OperationPlan(operations=tuple(all_operations)),
        )

    def folderize(self, folder_name: str) -> SequenceResult:
        """Prepare an operation to move all items to a subfolder.

        Args:
            folder_name: Name of the subfolder to create and move items to

        Returns:
            SequenceResult containing (new_sequence, plan)
        """
        new_directory = self.directory / folder_name
        return self.move(new_directory, create_directory=True)

    # -------------------------------------------------------------------------
    # Validation and analysis
    # -------------------------------------------------------------------------

    def find_duplicate_frames(self) -> Dict[int, Tuple[Item, ...]]:
        """Identifies frames that appear multiple times with different padding.

        Returns:
            Dictionary mapping frame numbers to tuples of duplicate Items.
            The first Item in each tuple has padding matching the sequence's
            standard padding.
        """
        frame_groups: Dict[int, List[Item]] = defaultdict(list)
        for item in self.items:
            frame_groups[item.frame_number].append(item)

        duplicates = {
            frame: items for frame, items in frame_groups.items() if len(items) > 1
        }

        sequence_padding = self.padding
        result: Dict[int, Tuple[Item, ...]] = {}

        for frame_number, items in duplicates.items():
            sorted_items = sorted(
                items,
                key=lambda x: (
                    x.padding != sequence_padding,
                    x.padding,
                    str(x),
                ),
            )
            result[frame_number] = tuple(sorted_items)

        return result

    def _validate_property_consistency(self, prop_name: str) -> Any:
        """Validates that all items have the same value for a property."""
        if not self.items:
            raise ValueError("Empty sequence")

        values = [getattr(item, prop_name) for item in self.items]
        first = values[0]
        if not all(v == first for v in values):
            raise AnomalousItemDataError(f"Inconsistent {prop_name} values")
        return first

    def validate(self) -> bool:
        """Validates that all items have consistent properties.

        Raises:
            AnomalousItemDataError: If any properties are inconsistent
        """
        self._validate_property_consistency(prop_name="prefix")
        self._validate_property_consistency(prop_name="extension")
        self._validate_property_consistency(prop_name="delimiter")
        self._validate_property_consistency(prop_name="suffix")
        self._validate_property_consistency(prop_name="directory")
        return True

    def _check_padding(self) -> bool:
        """Checks that all items have the same padding."""
        if not all(item.padding == self.padding for item in self.items):
            logger.debug("Inconsistent padding in sequence")
            return False
        return True


# =============================================================================
# Parsing Classes (unchanged from original)
# =============================================================================


class ItemParser:
    """Static utility class for parsing filenames and discovering sequences.

    Parser provides methods to analyze filenames, extract components, and
    group related files into sequences. It handles complex filename patterns
    and supports various file naming conventions commonly used in visual
    effects and animation pipelines.

    Class Attributes:
        pattern (str): Regex pattern for parsing frame-based filenames
        known_extensions (set): Set of compound file extensions (e.g., 'tar.gz')

    Example:
        Parser can handle filenames like:
        - "render_001.exr"
        - "comp.001.exr"
        - "anim-0100.png"
    """

    pattern = (
        r"^"
        r"(?P<name>.*?(?=[^a-zA-Z\d]*\d+(?!.*\d+)))"
        r"(?P<delimiter>[^a-zA-Z\d]*)"
        r"(?P<frame>\d+)"
        r"(?!.*\d+)"
        r"(?P<suffix>.*?)$"
    )

    known_extensions = {"tar.gz", "tar.bz2", "log.gz"}

    @staticmethod
    def item_from_filename(
        filename: str,
        directory: Optional[Path] = None,
        pattern: Optional[str] = None,
    ) -> Optional[Item]:
        """Parse a filename into an Item object.

        Args:
            filename: The filename to parse
            directory: Optional directory Path
            pattern: Optional custom regex pattern

        Returns:
            Item object if parsing succeeds, None if the filename doesn't match
        """
        if len(Path(filename).parts) > 1:
            raise ValueError("first argument must be a name, not a path")

        parts = filename.split(".")
        if len(parts) <= 1:
            name_part = filename
            extension = ""
        else:
            for i in range(len(parts) - 1):
                possible_ext = ".".join(parts[-(i + 1) :])
                if possible_ext in ItemParser.known_extensions:
                    name_part = ".".join(parts[: -(i + 1)])
                    extension = possible_ext
                    break
            else:
                name_part = ".".join(parts[:-1])
                extension = parts[-1]

        if not pattern:
            pattern = ItemParser.pattern

        match = re.match(pattern, name_part)
        if not match:
            return None

        parsed_dict = match.groupdict()
        parsed_dict.setdefault("frame", "")
        parsed_dict.setdefault("name", "")
        parsed_dict.setdefault("delimiter", "")
        parsed_dict.setdefault("suffix", "")

        name = parsed_dict["name"]
        delimiter = parsed_dict["delimiter"]

        if len(delimiter) > 1:
            name += delimiter[0:-1]
            delimiter = delimiter[-1]

        if directory is None:
            directory = Path("")

        return Item(
            prefix=name,
            frame_string=parsed_dict["frame"],
            extension=extension,
            delimiter=delimiter,
            suffix=parsed_dict["suffix"],
            directory=Path(directory),
        )

    @staticmethod
    def item_from_path(path: Path) -> Optional[Item]:
        """Creates an Item object from a Path object."""
        return ItemParser.item_from_filename(path.name, path.parent)

    @staticmethod
    def item_from_components(
        components: Components, frame: int, directory: Optional[Path] = None
    ) -> Item:
        """Converts a Components object into an Item object."""
        if isinstance(components, str):
            raise TypeError("components must be a Components object")

        if components.prefix is None:
            raise ValueError("components must have a prefix")

        if components.extension is None:
            raise ValueError("components must have an extension")

        if components.padding is not None:
            padding = components.padding
        else:
            padding = len(str(frame))
        frame_string = str(frame).zfill(padding)

        return Item(
            prefix=components.prefix,
            frame_string=frame_string,
            extension=components.extension,
            delimiter=components.delimiter,
            suffix=components.suffix,
            directory=directory,
        )

    @staticmethod
    def convert_padding_to_hashes(sequence_str: str) -> str:
        """Converts printf-style patterns (%04d) to hash notation (####)."""
        logger.debug("Converting printf pattern to hash notation")
        printf_pattern = r"%(?:(0)?(\d+))?d"

        def replace_match(match: re.Match) -> str:
            padding = match.group(2)
            if padding:
                return "#" * int(padding)
            else:
                return "#"

        return re.sub(printf_pattern, replace_match, sequence_str)


class SequenceParser:
    @dataclass
    class ParseResult:
        sequences: List[FileSequence]
        rogues: List[Path]

    class SequenceDictItem(TypedDict):
        name: str
        delimiter: str
        suffix: str
        frames: List[str]
        extension: str
        items: List[Item]

    @staticmethod
    def from_file_list(
        filename_list: List[str],
        min_frames: int,
        directory: Optional[Path] = None,
        allowed_extensions: Optional[set] = None,
    ) -> ParseResult:
        """Creates FileSequence objects from a list of filenames."""
        sequence_dict: Dict[
            Tuple[str, str, str, str], SequenceParser.SequenceDictItem
        ] = {}

        rogues: List[Path] = []

        if allowed_extensions:
            allowed_extensions = {ext.lower().lstrip(".") for ext in allowed_extensions}

        for file in filename_list:
            if file[0] == ".":
                continue

            if allowed_extensions:
                extension = Path(file).suffix.lower().lstrip(".")
                if extension not in allowed_extensions:
                    continue

            parsed_item = ItemParser.item_from_filename(file, directory)
            if not parsed_item:
                if directory is None:
                    directory = Path("")
                rogues.append(directory / file)
                continue

            key = (
                parsed_item.prefix,
                parsed_item.delimiter or "",
                parsed_item.suffix or "",
                parsed_item.extension or "",
            )

            if key not in sequence_dict:
                sequence_dict[key] = {
                    "name": parsed_item.prefix,
                    "delimiter": parsed_item.delimiter or "",
                    "suffix": parsed_item.suffix or "",
                    "frames": [],
                    "extension": parsed_item.extension or "",
                    "items": [],
                }

            sequence_dict[key]["items"].append(parsed_item)
            sequence_dict[key]["frames"].append(parsed_item.frame_string)

        sequence_list: List[FileSequence] = []

        for seq in sequence_dict.values():
            if len(seq["items"]) < min_frames:
                continue

            sorted_items = tuple(sorted(seq["items"], key=lambda i: i.frame_number))
            temp_sequence = FileSequence(items=sorted_items)

            duplicates = temp_sequence.find_duplicate_frames()

            if not duplicates:
                sequence_list.append(temp_sequence)
                continue

            padding_counts = Counter(item.padding for item in temp_sequence.items)
            nominal_padding = padding_counts.most_common(1)[0][0]

            main_sequence_items: List[Item] = []
            anomalous_items: Dict[int, List[Item]] = defaultdict(list)
            processed_frames: set = set()

            for item in temp_sequence.items:
                if item.frame_number in processed_frames:
                    continue

                if item.frame_number in duplicates:
                    duplicate_items = duplicates[item.frame_number]
                    for dup_item in duplicate_items:
                        if dup_item.padding == nominal_padding:
                            main_sequence_items.append(dup_item)
                        else:
                            anomalous_items[dup_item.padding].append(dup_item)
                else:
                    main_sequence_items.append(item)

                processed_frames.add(item.frame_number)

            if len(main_sequence_items) >= 2:
                sorted_main = sorted(main_sequence_items, key=lambda i: i.frame_number)
                main_sequence = FileSequence(items=tuple(sorted_main))
                sequence_list.append(main_sequence)

            for _padding, items_list in anomalous_items.items():
                if len(items_list) >= 2:
                    anomalous_sequence = FileSequence(
                        items=tuple(sorted(items_list, key=lambda i: i.frame_number))
                    )
                    sequence_list.append(anomalous_sequence)

        logger.info(f"Parsed {len(sequence_list)} sequences in {directory}")

        return SequenceParser.ParseResult(sequence_list, rogues)

    @staticmethod
    def filesequences_from_components_in_directory(
        components: Components, min_frames: int, directory: Path
    ) -> List[FileSequence]:
        """Matches components against a directory and returns matching sequences."""
        sequences = SequenceParser.from_directory(directory, min_frames).sequences

        matches: List[FileSequence] = []

        for sequence in sequences:
            if _sequence_matches_components(sequence, components):
                matches.append(sequence)

        logger.info("Found %d sequences matching %s", len(matches), str(components))
        return matches

    @staticmethod
    def match_sequence_string_in_filename_list(
        sequence_string: str,
        filename_list: List[str],
        min_frames: int,
        directory: Optional[Path] = None,
    ) -> Optional[FileSequence]:
        """Matches a sequence string against a list of filenames."""
        logger.debug("Pre padding conversion: %s", sequence_string)
        sequence_string = ItemParser.convert_padding_to_hashes(sequence_string)
        logger.debug("Post padding conversion: %s", sequence_string)

        sequences = SequenceParser.from_file_list(
            filename_list, min_frames, directory
        ).sequences

        matched: List[FileSequence] = []

        for sequence in sequences:
            if sequence.sequence_string == sequence_string:
                matched.append(sequence)

        if len(matched) > 1:
            raise ValueError(
                f"Multiple sequences match {sequence_string!r}: "
                f"{matched!r}, should be only one"
            )

        if len(matched) == 0:
            return None

        logger.info("Found sequences matching %s", sequence_string)
        return matched[0]

    @staticmethod
    def match_sequence_string_absolute(
        path: str, min_frames: int
    ) -> Optional[FileSequence]:
        """Matches a sequence path and returns a FileSequence object."""
        path_ = Path(path)
        return SequenceParser.match_sequence_string_in_directory(
            path_.name, min_frames, path_.parent
        )

    @staticmethod
    def match_sequence_string_in_directory(
        filename: str,
        min_frames: int,
        directory: Path,
    ) -> Optional[FileSequence]:
        """Matches a sequence string against a directory's contents."""
        logger.debug("Matching sequence string in directory: %s", filename)
        files = os.listdir(str(directory))
        return SequenceParser.match_sequence_string_in_filename_list(
            filename, files, min_frames, directory
        )

    @staticmethod
    def from_directory(
        directory: Path,
        min_frames: int,
        allowed_extensions: Optional[set] = None,
    ) -> ParseResult:
        """Scans a directory and returns detected sequences."""
        files = [str(f.name) for f in directory.iterdir() if f.is_file()]

        if not isinstance(files, list):
            raise TypeError("files must be a list")

        if not isinstance(directory, Path):
            raise TypeError("directory must be a Path object")

        return SequenceParser.from_file_list(
            files, min_frames, directory, allowed_extensions
        )

    @staticmethod
    def match_components_in_filename_list(
        components: Components,
        filename_list: List[str],
        min_frames: int,
        directory: Optional[Path] = None,
    ) -> List[FileSequence]:
        """Matches components against a list of filenames."""
        sequences = SequenceParser.from_file_list(
            filename_list, min_frames, directory
        ).sequences

        matches: List[FileSequence] = []

        for sequence in sequences:
            if _sequence_matches_components(sequence, components):
                matches.append(sequence)

        logger.info("Found %d sequences matching %s", len(matches), str(components))
        return matches


def _sequence_matches_components(sequence: FileSequence, comp: Components) -> bool:
    """Check if a sequence matches the given components specification."""
    if comp.prefix is not None and comp.prefix != sequence.prefix:
        return False
    if comp.delimiter is not None and comp.delimiter != sequence.delimiter:
        return False
    if comp.padding is not None and comp.padding != sequence.padding:
        return False
    if comp.suffix is not None and comp.suffix != sequence.suffix:
        return False
    if comp.extension is not None and comp.extension != sequence.extension:
        return False
    return True


# =============================================================================
# Problems and Exceptions
# =============================================================================


class Problems(Flag):
    """Enumeration of potential issues in frame sequences.

    Uses Flag for bitwise operations to track multiple issues.

    Flags:
        NONE: No problems detected
        MISSING_FRAMES: Sequence has gaps between frame numbers
        INCONSISTENT_PADDING: Frame numbers have different padding lengths
        FILE_NAME_INCLUDES_SPACES: Filenames contain spaces
        DUPLICATE_FRAME_NUMBERS_WITH_INCONSISTENT_PADDING: Same frame, different padding

    Example:
        problems = Problems.check_sequence(sequence)
        if problems & Problems.MISSING_FRAMES:
            print("Sequence has missing frames")
    """

    NONE = 0
    MISSING_FRAMES = auto()
    INCONSISTENT_PADDING = auto()
    FILE_NAME_INCLUDES_SPACES = auto()
    DUPLICATE_FRAME_NUMBERS_WITH_INCONSISTENT_PADDING = auto()

    @classmethod
    def check_sequence(cls, sequence: FileSequence) -> Problems:
        """Analyze a FileSequence and return a Problems flag."""
        problems = cls.NONE

        if sequence.missing_frames:
            problems |= cls.MISSING_FRAMES

        if not sequence._check_padding():
            problems |= cls.INCONSISTENT_PADDING

        if any(" " in item.filename for item in sequence.items):
            problems |= cls.FILE_NAME_INCLUDES_SPACES

        if sequence.find_duplicate_frames():
            problems |= cls.DUPLICATE_FRAME_NUMBERS_WITH_INCONSISTENT_PADDING

        return problems


class AnomalousItemDataError(Exception):
    """Raised when unacceptable inconsistent data is found in a FileSequence."""


# =============================================================================
# Factory Class
# =============================================================================


class SequenceFactory:
    """Factory for creating FileSequence objects from various sources."""

    @staticmethod
    def from_directory(directory: Path, min_frames: int = 2) -> List[FileSequence]:
        return SequenceParser.from_directory(directory, min_frames).sequences

    @staticmethod
    def from_filenames(
        filenames: List[str], min_frames: int = 2, directory: Optional[Path] = None
    ) -> List[FileSequence]:
        """Creates FileSequence objects from a list of filenames."""
        return SequenceParser.from_file_list(filenames, min_frames, directory).sequences

    @staticmethod
    def from_filenames_with_components(
        components: Components,
        filename_list: List[str],
        directory: Optional[Path] = None,
        min_frames: int = 2,
    ) -> List[FileSequence]:
        return SequenceParser.match_components_in_filename_list(
            components, filename_list, min_frames, directory
        )

    @staticmethod
    def from_directory_with_components(
        components: Components, directory: Path, min_frames: int = 2
    ) -> List[FileSequence]:
        """Matches components against a directory's contents."""
        return SequenceParser.filesequences_from_components_in_directory(
            components, min_frames, directory
        )

    @staticmethod
    def from_filenames_with_sequence_string(
        sequence_string: str,
        filename_list: List[str],
        directory: Optional[Path] = None,
        min_frames: int = 2,
    ) -> Optional[FileSequence]:
        """Matches a sequence string against a list of filenames."""
        return SequenceParser.match_sequence_string_in_filename_list(
            sequence_string, filename_list, min_frames, directory
        )

    @staticmethod
    def from_sequence_string_absolute(
        path: str, min_frames: int = 2
    ) -> Optional[FileSequence]:
        """Parses a combined directory and sequence string."""
        return SequenceParser.match_sequence_string_absolute(path, min_frames)

    @staticmethod
    def from_directory_with_sequence_string(
        filename: str, directory: Path, min_frames: int = 2
    ) -> Optional[FileSequence]:
        """Matches a sequence string against a directory's contents."""
        return SequenceParser.match_sequence_string_in_directory(
            filename, min_frames, directory
        )

    @staticmethod
    def from_nuke_node(node: Any) -> Optional[FileSequence]:
        """Creates a FileSequence from a Nuke node.

        Can only be called from a Nuke environment.

        Raises:
            ImportError: If Nuke is not available
        """
        if not importlib.util.find_spec("nuke"):
            raise ImportError("This method can only be called from a Nuke environment")
        return SequenceFactory.from_sequence_string_absolute(node["file"].getValue())


class SequenceBuilder:
    """
    A fluent wrapper for FileSequence that accumulates operations.
    
    Allows chaining multiple operations (rename -> move -> offset) 
    into a single atomic Plan without executing them immediately.
    """
    def __init__(self, sequence: FileSequence):
        self._current_sequence = sequence
        self._accumulated_plan = OperationPlan.empty()

    @property
    def current_sequence(self) -> FileSequence:
        """The state of the sequence as it would look after operations."""
        return self._current_sequence

    @property
    def plan(self) -> OperationPlan:
        """The total accumulated plan so far."""
        return self._accumulated_plan

    def rename(self, new_name: Components) -> "SequenceBuilder":
        """Plan a rename and update internal state."""
        # We rely on your existing SequenceResult class for the logic
        result = self._current_sequence.rename(new_name)
        self._update_state(result)
        return self

    def move(self, new_directory: Path, create_directory: bool = False) -> "SequenceBuilder":
        """Plan a move and update internal state."""
        result = self._current_sequence.move(new_directory, create_directory)
        self._update_state(result)
        return self

    def copy(self, 
             new_name: Optional[Components] = None, 
             new_directory: Optional[Path] = None,
             create_directory: bool = False) -> "SequenceBuilder":
        """Plan a copy and update internal state."""
        result = self._current_sequence.copy(new_name, new_directory, create_directory)
        self._update_state(result)
        return self

    def offset_frames(self, offset: int, padding: Optional[int] = None) -> "SequenceBuilder":
        """Plan a frame offset and update internal state."""
        result = self._current_sequence.offset_frames(offset, padding)
        self._update_state(result)
        return self

    def with_padding(self, padding: int) -> "SequenceBuilder":
        """Plan a padding change and update internal state."""
        result = self._current_sequence.with_padding(padding)
        self._update_state(result)
        return self
    
    def folderize(self, folder_name: str) -> "SequenceBuilder":
        """Plan moving items into a subfolder."""
        result = self._current_sequence.folderize(folder_name)
        self._update_state(result)
        return self

    def delete(self) -> OperationPlan:
        """
        Plan a delete. 
        
        Note: This is a terminal operation for the builder chain 
        because you cannot manipulate a sequence after it is deleted.
        Returns the accumulated plan plus the delete operation.
        """
        delete_plan = self._current_sequence.delete()
        return self._accumulated_plan + delete_plan

    def build(self) -> SequenceResult:
        """Return the final proposed state and the total plan."""
        return SequenceResult(self._current_sequence, self._accumulated_plan)

    def execute(self, force: bool = False) -> ExecutionResult:
        """Execute all accumulated operations at once."""
        return self._accumulated_plan.execute(force=force)

    # --- Helper ---
    def _update_state(self, result: SequenceResult) -> None:
        """Update the internal sequence and add to the plan."""
        self._current_sequence = result.sequence
        self._accumulated_plan += result.plan