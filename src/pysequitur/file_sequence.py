# Copyright (c) 2024 Alex Harding (alexharding.ooo)
# This file is part of PySequitur which is released under MIT license.
# See file LICENSE for full license details.

import re
import os
import shutil
import logging
from enum import Flag, auto
from typing import Dict, Optional, Tuple, List, Any, TypedDict
from pathlib import Path
from dataclasses import dataclass
from collections import Counter, defaultdict
from operator import attrgetter

logging.basicConfig(
    level=logging.INFO,  # Set default level to INFO
    format="%(levelname)s: %(message)s",  # Simple format
)

logger = logging.getLogger("pysequitur")


@dataclass
class Components:
    """Configuration class for naming operations on Items and FileSequences.

    Provides a flexible way to specify components of a filename during renaming
    or parsing operations.

    Any component left as None will retain its original value.

    Attributes:
        prefix (str, optional): New base name
        delimiter (str, optional): New separator between name and frame number
        padding (int, optional): New frame number padding length
        suffix (str, optional): New suffix after frame number
        extension (str, optional): New file extension

    Example:
        Renamer(prefix="new_name", padding=4) would change:
        "old_001.exr" to "new_name_0001.exr"

    """

    prefix: Optional[str] = None
    delimiter: Optional[str] = None
    padding: Optional[int] = None
    suffix: Optional[str] = None
    extension: Optional[str] = None
    frame_number: Optional[int] = None


@dataclass
class Item:

    prefix: str
    frame_string: str
    extension: str
    delimiter: Optional[str] = None
    suffix: Optional[str] = None
    directory: Optional[Path] = None

    def __post_init__(self) -> None:
        if self.suffix is not None and any(char.isdigit() for char in self.suffix):
            raise ValueError("suffix cannot contain digits")

        self._dirty = False
        if self.directory is None:
            self.directory = ""

        if isinstance(self.directory, str):
            raise ValueError("directory must be a Path object")

    @staticmethod
    def from_path(
        path: Path | str,
        directory: Optional[Path] = None,
    ) -> "Item | None":
        """Creates an Item object from a Path object, or a string representing
        the file name, with an optional string representing the directory.

        Args:
            path (Path | str): Path object or string representing the file name
            directory (str, optional): Directory to use if path is a string (optional)
            pattern (str, optional): Pattern to use for parsing if path is a string (optional)

        """

        return Parser.item_from_filename(path, directory)

    @staticmethod
    def from_components(
        components: Components, frame: int, directory: Optional[Path] = None
    ) -> "Item":
        return Parser.item_from_components(components, frame, directory)

    @property
    def path(self) -> Path:
        return Path(self.absolute_path)

    @property
    def filename(self) -> str:
        """Returns the filename of the item as a string."""
        # if not self.exists:
        #     raise FileNotFoundError()

        s = self.delimiter if self.delimiter else ""
        p = self.suffix if self.suffix else ""
        e = f".{self.extension}" if self.extension else ""

        return f"{self.prefix}{s}{self.frame_string}{p}{e}"

    @property
    def absolute_path(self) -> Path:
        """Returns the absolute path of the item as a Path object."""
        return Path(self.directory) / self.filename

    @property
    def padding(self) -> int:
        """Returns the padding of the frame number as an integer."""
        return len(self.frame_string)

    @padding.setter
    def padding(self, value: int) -> None:
        """Sets the padding of the frame number.

        Args:
            value (int): New padding
        """
        # TODO test this
        # TODO write test for unlinked item


        padding = max(value, len(str(self.frame_number)))
        # self.frame_string = f"{self.frame_number:0{padding}d}"
        self.rename(Components(padding=padding))


    @property
    def stem(self) -> str:
        """Returns the stem of the item as a string."""
        return self.path.stem

    @property
    def frame_number(self) -> int:
        """Returns the frame number as an integer."""
        return int(self.frame_string)

    def set_frame_number(
        self, new_frame_number: int, padding: Optional[int] = None
    ) -> None:
        """Sets the frame number of the item.

        Args:
            new_frame_number (int): New frame number
            padding (int, optional): New frame number padding

        Raises:
            ValueError: If new_frame_number is negative

        """

        # TODO test this

        if new_frame_number == self.frame_number and padding == self.padding:
            return

        if new_frame_number < 0:
            raise ValueError("new_frame_number cannot be negative")

        if padding is None:
            padding = self.padding

        new_padding = max(padding, len(str(new_frame_number)))
        print("\n_-_-_ new padding ")
        print(new_padding)
        # self.frame_string = f"{new_frame_number:0{new_padding}d}"

        self.rename(Components(frame_number=new_frame_number, padding=new_padding))

    def move(self, new_directory: Path) -> None:
        """Moves the item to a new directory.

        # Args:
        #     new_directory (str): New directory

        #"""

        logger.info("Moving %s to %s", self.filename, new_directory)

        if self.path.exists():
            new_path = Path(new_directory) / self.filename
            self.path.rename(new_path)
            self.directory = new_directory

        else:
            raise FileNotFoundError()

    def check_move(self, new_directory: Path):
        new_path = Path(new_directory) / self.filename
        return (self.absolute_path, new_path, new_path.exists())  # TODO test this

    def rename(
        self, new_name: Components
    ) -> None:  # TODO remove the optional string argument, force components
        """Renames the item.

        Any component that is None will not be changed.

        Can be used with an empty Components object to force the Path object to be renamed to the
        computed file name value from the components.

        # Args:
        #     new_name (str | Components, optional): New name

        #"""

        logger.info("Renaming %s to %s", self.filename, new_name)

        # if not self.path.exists():
        #     raise FileNotFoundError()  # TODO this should support unlinked item

        # path is generated dynamically so we store the old one so we
        # can use it for rename operation
        old_path = Path(str(self.path))

        # print("\n!=!=!=")
        # print(self.filename)
        # print(self.absolute_path)
        # print(old_path)
        # print(old_path.exists())

        if new_name is None:
            new_name = Components()


        if isinstance(new_name, str): #TODO remove this
            # self.prefix = new_name
            # self.path = self.path.rename(self.path.with_name(self.filename))
            new_name = Components(prefix=new_name)
            # return

        new_name = self._complete_components(new_name)

        # Update internal state
        self.prefix = new_name.prefix
        self.delimiter = new_name.delimiter
     
        self.suffix = new_name.suffix
        self.extension = new_name.extension
        new_padding = max(new_name.padding, len(str(new_name.frame_number)))
        self.frame_string = f"{new_name.frame_number:0{new_padding}d}"

        if old_path.exists():
            old_path.rename(old_path.with_name(self.filename))
        else:
            Warning(f"Renaming {self.filename} which does not exist")

    def check_rename(
        self, new_name: Components
    ) -> None:  # TODO remove the optional string argument, force components

        # if new_name is None:
        #     new_name = Components()

        # if isinstance(new_name, str):
        #     new_name = Components(prefix=new_name)

        new_name = self._complete_components(new_name)
        potential_item = Item.from_components(
            new_name, self.frame_number, self.directory
        )

        return (self.absolute_path, potential_item.absolute_path, potential_item.exists)

    def _complete_components(self, components: Components) -> Components:
        return Components(
            prefix=components.prefix if components.prefix is not None else self.prefix,
            delimiter=(
                components.delimiter
                if components.delimiter is not None
                else self.delimiter
            ),
            padding=(
                components.padding if components.padding is not None else self.padding
            ),
            suffix=components.suffix if components.suffix is not None else self.suffix,
            extension=(
                components.extension
                if components.extension is not None
                else self.extension
            ),
            frame_number=(
                components.frame_number
                if components.frame_number is not None
                else self.frame_number
            ),
        )

    def copy(
        self, new_name: Optional[str], new_directory: Optional[Path] = None
    ) -> "Item":
        """Copies the item.

        Args:
            new_name (str): New name
            new_directory (str, optional): New directory

        # Returns:
        #     Item: New item

        #"""

        logger.info("Copying %s to %s", self.filename, new_name)

        if not self.path.exists():
            raise FileNotFoundError()

        if isinstance(new_name, str):
            new_name = self._complete_components(Components(prefix=new_name))

        new_item = Item.from_components(new_name, self.frame_number, new_directory)

        if new_item.absolute_path == self.absolute_path:
            new_item.rename(new_name.prefix + "_copy")

        if new_item.exists:
            raise FileExistsError()  # TODO test this

        shutil.copy2(self.absolute_path, new_item.absolute_path)

        return new_item

        ## old way

        # if isinstance(new_name, str):
        #     new_item = Item(
        #         prefix=new_name,
        #         frame_string=self.frame_string,
        #         extension=self.extension,
        #         path=self.path,
        #         delimiter=self.delimiter,
        #         suffix=self.suffix,
        #     )
        # elif isinstance(new_name, Components):
        #     new_item = Item(
        #         prefix=(
        #             new_name.prefix if new_name.prefix is not None else self.prefix
        #         ),
        #         frame_string=self.frame_string,
        #         extension=(
        #             new_name.extension
        #             if new_name.extension is not None
        #             else self.extension
        #         ),
        #         path=self.path,
        #         delimiter=(
        #             new_name.delimiter
        #             if new_name.delimiter is not None
        #             else self.delimiter
        #         ),
        #         suffix=(
        #             new_name.suffix if new_name.suffix is not None else self.suffix
        #         ),
        #     )
        #     if new_name.padding is not None:
        #         padding = max(new_name.padding, self._min_padding)
        #         new_item.frame_string = f"{self.frame_number:0{padding}d}"
        # else:
        #     raise ValueError("new_name must be a string or a Renamer object")

        # if new_directory is not None:
        #     new_path = Path(new_directory) / new_item.filename
        # else:
        #     new_path = self.path.with_name(new_item.filename)

        # if new_path == self.path:
        #     new_item.prefix += "copy"
        #     new_path = new_path.with_name(new_item.filename)

        # shutil.copy(str(self.path), str(new_path))
        # new_item.path = new_path

        # return new_item

    def check_copy(self, new_name: Optional[str], new_directory: Optional[Path] = None):

        # TODO test this

        if isinstance(new_name, str):
            new_name = self._complete_components(Components(prefix=new_name))

        new_item = Item.from_components(new_name, self.frame_number, new_directory)

        if new_item.absolute_path == self.absolute_path:
            new_item.rename(new_name.prefix + "_copy")

        return (self.absolute_path, new_item.absolute_path, new_item.exists)

    def delete(self) -> None:
        """Deletes the item, including the associated file."""

        logger.info("Deleting %s", self.filename)

        if self.path.exists():
            self.path.unlink()
        else:
            raise FileNotFoundError()

    @property
    def exists(self) -> bool:
        """Checks if the item exists.

        Returns:
            bool: True if the item exists

        """

        return self.path.exists()

    # @property
    # def directory(self) -> Path:
    #     """Returns the directory containing the item."""

    #     return self.path.parent

    @property
    def _min_padding(self) -> int:
        """Computes the minimum padding required to represent the frame
        number."""
        return len(str(int(self.frame_string)))

    def _check_path(self) -> bool:
        """Checks if the path computed from the components matches the path
        object."""

        if not self.path.exists():
            raise FileNotFoundError()

        if not self.absolute_path == str(self.path):
            return False

        return True


@dataclass
class FileSequence:
    """Manages a collection of related Items that form an image sequence.

    FileSequence provides methods for manipulating multiple related files as a single unit,
    including operations like renaming, moving, and frame number manipulation. It also
    provides validation and analysis of the sequence's health and consistency.

    Attributes:
        items (list[Item]): List of Item objects that make up the sequence

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

    items: list[Item]

    def __str__(self) -> str:
        result = ""
        for item in self.items:
            result += str(item) + "\n"

        return result

    @property
    def actual_frame_count(self) -> int:
        """Returns the total number of frames in the sequence, taking missing
        frames into account."""
        return len(self.items)

    @property
    def first_frame(self) -> int:
        """Returns the lowest frame number in the sequence."""
        return min(self.items, key=lambda item: item.frame_number).frame_number

    @property
    def last_frame(self) -> int:
        """Returns the highest frame number in the sequence."""
        return max(self.items, key=lambda item: item.frame_number).frame_number

    @property
    def prefix(self) -> str:
        """Returns the prefix Performs a check to ensure that prefix is
        consistent across all items."""

        return str(self._check_consistent_property(prop_name="prefix"))

    @property
    def extension(self) -> str:
        """Returns the extension Performs a check to ensure that extension is
        consistent across all items."""
        return str(self._check_consistent_property(prop_name="extension"))

    @property
    def delimiter(self) -> str:
        """Returns the delimiter Performs a check to ensure that delimiter is
        consistent across all items."""
        return str(self._check_consistent_property(prop_name="delimiter"))

    @property
    def suffix(self) -> str:
        """Returns the suffix Performs a check to ensure that suffix is
        consistent across all items."""
        return str(self._check_consistent_property(prop_name="suffix"))

    @property
    def directory(self) -> str:
        """Returns the directory Performs a check to ensure that directory is
        consistent across all items."""
        return str(self._check_consistent_property(prop_name="directory"))

    @property
    def existing_frames(self) -> list[int]:
        """Returns a list of frame numbers which are present in the sequence.

        Frames are determined by parsing the filename of each item in the
        sequence.

        """
        return [item.frame_number for item in self.items]

    @property
    def missing_frames(self) -> set:
        """Returns a set of frame numbers which are not present in the sequence.

        Frames are determined to be missing if they fall within the range of the
        first and last frame of the sequence (inclusive), but are not present in
        the sequence.

        """

        missing_frames = set(range(self.first_frame, self.last_frame + 1)) - set(
            self.existing_frames
        )

        # if missing_frames:
        #     logging.warning("Missing frames: %s", missing_frames)

        return missing_frames

    @property
    def frame_count(self) -> int:
        """Returns the number of frames in the sequence."""
        return self.last_frame + 1 - self.first_frame

    @property
    def padding(self) -> int:
        """Returns the padding.

        If padding is inconsistent, the most common padding is returned

        """

        # self._check_padding()

        if not self.items:
            raise ValueError("No items in sequence")
        padding_counts = Counter(item.padding for item in self.items)

        return padding_counts.most_common(1)[0][0]

    @property
    def file_name(self) -> str:
        """Returns the file name, computed from the components."""
        padding = "#" * self.padding
        return f"{self.prefix}{self.delimiter}{padding}{self.suffix}.{self.extension}"

    @property
    def absolute_file_name(self) -> str:
        """Returns the absolute file name."""
        return os.path.join(self.directory, self.file_name)

    @property
    def problems(self) -> "Problems":
        """Returns a flag containing all detected problems."""

        problems = Problems.check_sequence(self)

        # if problems is not Problems.NONE:
        #     logging.warning("Problems found: %s", problems)

        return problems

    @staticmethod
    def from_file_list(
        filename_list: List[str],
        directory: Optional[Path] = None,
    ) -> List["FileSequence"]:
        """
        Creates a list of detected FileSequence objects from a list of filenames.

        If no directory is supplied, the pathlib.Path objects cannot be verified
        and the sequence is considered virtual.

        Args:
            filename_list (List[str]): A list of filenames to be analyzed for sequences.
            directory (str, optional): The directory in which filenames are located.


        Returns:
            List[FileSequence]: A list of FileSequence objects representing the detected file sequences.

        """
        return Parser.filesequences_from_file_list(filename_list, directory)

    @staticmethod
    def from_directory(directory: str | Path) -> List["FileSequence"]:
        """
        Creates a list of detected FileSequence objects from files found in a given directory.

        Args:
            directory (str | Path): The directory in which to search for sequences.

        Returns:
            FileSequence: A list of FileSequence objects representing the detected file sequences.
        """
        return Parser.filesequences_from_directory(directory)

    @staticmethod
    def from_components_in_filename_list(
        components: Components,
        filename_list: List[str],
        directory: Optional[Path] = None,
    ) -> List["FileSequence"]:
        """
        Matches components against a list of filenames and returns a list of detected
        sequences as FileSequence objects. If no components are specified, all
        possible sequences are returned. Otherwise only sequences that match the
        specified components are returned.

        If no directory is supplied, the pathlib.Path objects cannot be verified
        and the sequence is considered virtual.

        Examples:

        >>> FileSequence.from_components_in_filename_list(Components(prefix = "image), filename_list)
            Returns all sequences with prefix "image"

        >>> FileSequence.from_components_in_filename_list(Components(prefix = "image", extension = "exr"), filename_list)
            Returns all sequences with prefix "image" and extension "exr"

        Args:
            components (Components): Components to match
            directory (str): Directory that contains the files

        Returns:
            list[FileSequence]: List of Sequence objects

        """
        return Parser.filesequences_from_components_in_filename_list(
            components, filename_list, directory
        )

    @staticmethod
    def from_components_in_directory(
        components: Components, directory: Path
    ) -> List["FileSequence"]:
        """
        Matches components against the contents of a directory and returns a list of detected
        sequences as FileSequence objects. If no components are specified, all
        possible sequences are returned. Otherwise only sequences that match the
        specified components are returned.


        Examples:

        >>> FileSequence.from_components_in_filename_list(Components(prefix = "image), filename_list)
            Returns all sequences with prefix "image"

        >>> FileSequence.from_components_in_filename_list(Components(prefix = "image", extension = "exr"), filename_list)
            Returns all sequences with prefix "image" and extension "exr"

        Args:
            components (Components): Components to match
            directory (str): Directory that contains the files

        Returns:
            list[FileSequence]: List of Sequence objects

        """
        return Parser.filesequences_from_components_in_directory(components, directory)

    @staticmethod
    def from_sequence_filename(
        filename: str, filename_list: List[str], directory: Optional[Path] = None
    ) -> "FileSequence":
        """
        Matches a sequence file name against a list of filenames and returns
        a detected sequence as a FileSequence object.

        Sequence filenames take the form: <prefix><delimiter><####><suffix>.<extension>
        where the number of # symbols determines the padding.

        Supported Examples:

        image.####.exr
        render_###_revision.jpg
        plate_v1-#####.png

        Digits in the suffix are not supported.

        Args:
            filename (str): Sequence file name
            filename_list (list): List of filenames
            directory (str): Directory that contains the files (optional)
            pattern (str): Regex pattern for parsing frame-based filenames (optional)

        Returns:
            FileSequence: Sequence object

        """
        return Parser.filesequence_from_sequence_string(
            filename, filename_list, directory
        )

    @staticmethod
    def from_sequence_filename_in_directory(
        filename: str, directory: Path
    ) -> "FileSequence":
        """
        Matches a sequence file name against a list of files in a given directory
        and returns a detected sequence as a FileSequence object.

        Sequence filenames take the form: <prefix><delimiter><####><suffix>.<extension>
        where the number of # symbols determines the padding.

        Supported Examples:

        image.####.exr
        render_###_revision.jpg
        plate_v1-#####.png

        Digits in the suffix are not supported.

        Args:
            filename (str): Sequence file name
            filename_list (list): List of filenames
            directory (str): Directory that contains the files (optional)
            pattern (str): Regex pattern for parsing frame-based filenames (optional)

        Returns:
            FileSequence: Sequence object

        """

        return Parser.filesequence_from_sequence_filename_in_directory(
            filename, directory
        )

    def rename(self, new_name: Components) -> None: #TODO refactor to use Components
        """Renames all items in the sequence.

        Args:
            new_name (str): The new name

        """
        if isinstance(new_name, str):
            raise ValueError(
                "new_name must be a Components object, not a string"
            )


        # TODO check if any of the new filesnames collide with existing files before proceeding

        self._validate()

        # print(self.items[0])

        for item in self.items:
            item.rename(new_name)

        # print(self.items[0])

    def move(self, new_directory: Path) -> None:
        """Moves all items in the sequence to a new directory.

        Args:
            new_directory (str): The directory to move the sequence to.

        """

        # TODO check if any of the new filesnames collide with existing files before proceeding

        for item in self.items:
            item.move(new_directory)

    def delete(self) -> None:
        """Deletes all files in the sequence."""

        for item in self.items:
            item.delete()

    def copy(
        self, new_name: str, new_directory: Optional[Path] = None
    ) -> "FileSequence":
        """Creates a copy of the sequence with a new name and optional new
        directory.

        Args:
            new_name (str): The new name
            new_directory (str, optional): The new directory. Defaults to None.

        Returns:
            FileSequence: A new FileSequence object representing the copied sequence

        """

        # TODO check if any of the new filesnames collide with existing files before proceeding

        self._validate()

        new_items = []
        for item in self.items:
            new_item = item.copy(new_name, new_directory)
            new_items.append(new_item)

        new_sequence = FileSequence(new_items)
        return new_sequence

    def offset_frames(self, offset: int, padding: Optional[int] = None) -> None:
        """Offsets all frames in the sequence by a given offset.

        If padding is not provided, the sequence's standard padding is used.

        Raises:
            ValueError: If the offset would result in a frame number below 0

        Args:
            offset (int): The offset to apply
            padding (int, optional): The padding to use. Defaults to None.

        """

        # TODO check if any of the new filesnames collide with existing files before proceeding

        if offset == 0:
            return

        if self.first_frame + offset < 0:
            raise ValueError("offset would yield negative frame numbers")

        if padding is None:
            padding = self.padding

        padding = max(padding, len(str(self.last_frame + offset)))

        for item in sorted(
            self.items, key=attrgetter("frame_number"), reverse=offset > 0
        ):

            target = item.frame_number + offset

            if any(item.frame_number == target for item in self.items):
                raise ValueError(f"Frame {target} already exists")

            item.set_frame_number(item.frame_number + offset, padding)

    def set_padding(self, padding: int = 0) -> None:
        """Sets the padding for all frames in the sequence.

        Defaults to minimum required padding to represent the last frame if a value below that is provided

        Args:
            padding (int, optional): The padding to set. Defaults to 0.

        """
        padding = max(padding, len(str(self.last_frame)))

        for item in self.items:
            item.padding = padding

    def find_duplicate_frames(self) -> Dict[int, Tuple[Item, ...]]:
        """Identifies frames that appear multiple times with different padding.
        For each set of duplicates, the first item in the tuple will be the one
        whose padding matches the sequence's standard padding.

        Returns:
            Dict[int, Tuple[Item, ...]]: Dictionary mapping frame numbers to tuples
            of Items representing duplicate frames. The first Item in each tuple
            has padding matching the sequence's standard padding.

        Example:
            If a sequence contains frame 1 as "001.ext", "01.ext", and "1.ext",
            and the sequence's padding is 3, the result would be:
            {1: (Item("001.ext"), Item("01.ext"), Item("1.ext"))}

        """
        # Group items by frame number
        frame_groups = defaultdict(list)
        for item in self.items:
            frame_groups[item.frame_number].append(item)

        # Filter for only the frame numbers that have duplicates
        duplicates = {
            frame: items for frame, items in frame_groups.items() if len(items) > 1
        }

        # Sort each group of duplicates
        sequence_padding = self.padding
        result = {}

        for frame_number, items in duplicates.items():
            # Sort items so that those matching sequence padding come first,
            # then by padding length, then by string representation for stability
            sorted_items = sorted(
                items,
                key=lambda x: (
                    x.padding != sequence_padding,  # False sorts before True
                    x.padding,
                    str(x),
                ),
            )
            result[frame_number] = tuple(sorted_items)

        return result

    def folderize(self, folder_name: str) -> None:
        """Moves all items in the sequence to a new directory.

        Args:
            folder_name (str): The directory to move the sequence to.

        """
        raise NotImplementedError

    def _check_consistent_property(self, prop_name: str) -> Any:
        """Checks if all items in the sequence have the same value for a given
        property.

        Args:
            prop_name (str): The name of the property to check.

        Returns:
            Any: The value of the property on the first item in the sequence.

        Raises:
            ValueError: If the sequence is empty.
            AnomalousItemDataError: If the values of the property are not consistent.

        """
        if not self.items:
            raise ValueError("Empty sequence")

        values = [getattr(item, prop_name) for item in self.items]

        first = values[0]
        if not all(v == first for v in values):
            raise AnomalousItemDataError(f"Inconsistent {prop_name} values")
        return first

    def _validate(self) -> None:
        """Checks that all items in the sequence have consistent values for the
        prefix, extension, delimiter, suffix, and directory properties.

        Raises:
            AnomalousItemDataError: If any of the properties have inconsistent
                values.

        """
        self._check_consistent_property(prop_name="prefix")
        self._check_consistent_property(prop_name="extension")
        self._check_consistent_property(prop_name="delimiter")
        self._check_consistent_property(prop_name="suffix")
        self._check_consistent_property(prop_name="directory")

    def _check_padding(self) -> bool:
        """Checks that all items in the sequence have the same padding.

        # Returns:
        #     bool: True if padding is consistent, False otherwise.

        #"""
        if not all(item.padding == self.padding for item in self.items):
            logger.warning("Inconsistent padding in sequence")
            return False
        return True


class Parser:
    """Static utility class for parsing filenames and discovering sequences.

    Most functionality is available through convenience methods in the Parser class.

    Parser provides methods to analyze filenames, extract components, and group related
    files into sequences. It handles complex filename patterns and supports various
    file naming conventions commonly used in visual effects and animation pipelines.

    Class Attributes:
        pattern (str): Regex pattern for parsing frame-based filenames
        known_extensions (set): Set of compound file extensions (e.g., 'tar.gz')

    Methods:
        parse_filename: Parse a single filename into components
        find_sequences: Group multiple files into sequences
        scan_directory: Scan a directory for frame sequences

    Example:
        Parser can handle filenames like:
        - "render_001.exr"
        - "comp.001.exr"
        - "anim-0100.png"

    """

    pattern = (
        r"^"
        # Name up to last frame number
        r"(?P<name>.*?(?=[^a-zA-Z\d]*\d+(?!.*\d+)))"
        # Separator before frame (optional)
        r"(?P<separator>[^a-zA-Z\d]*)"
        # Frame number (1 or more digits)
        r"(?P<frame>\d+)"
        # Negative lookahead for more digits
        r"(?!.*\d+)"
        # Non-greedy match up to extension
        r"(?P<post_numeral>.*?)"
        # Dot and extension (everything after last dot)
        r"(?:\.(?P<ext>.*))?$"
    )

    known_extensions = {"tar.gz", "tar.bz2", "log.gz"}

    @staticmethod
    def item_from_filename(
        filename: str | Path,
        directory: Optional[Path] = None,
        pattern: Optional[str] = None,
    ) -> Item | None:
        """Parse a single filename into components.

        Args:
            filename (str | Path): Filename to parse
            directory (str, optional): Directory of the file. Defaults to None.
            pattern (str, optional): Regex pattern for parsing. Defaults to None.

        Returns:
            Item: Parsed filename components

        """

        if isinstance(filename, Path):
            directory = str(filename.parent)
            filename = str(filename.name)

        if len(Path(filename).parts) > 1:
            raise ValueError("first argument must be a name, not a path")

        if not pattern:
            pattern = Parser.pattern

        match = re.match(pattern, filename)
        if not match:
            return None

        parsed_dict = match.groupdict()

        # Set default values if keys are missing
        parsed_dict.setdefault("frame", "")
        parsed_dict.setdefault("name", "")
        parsed_dict.setdefault("ext", "")
        parsed_dict.setdefault("separator", "")
        parsed_dict.setdefault("post_numeral", "")

        name = parsed_dict["name"]
        delimiter = parsed_dict["separator"]

        if len(delimiter) > 1:
            name += delimiter[0:-1]
            delimiter = delimiter[-1]

        if directory is None:
            directory = Path("")
        # path = Path(os.path.join(directory, filename))
        path = Path(directory) / filename

        if not path:
            raise ValueError("invalid filepath")

        ext = parsed_dict.get("ext", "")

        if parsed_dict["ext"]:
            # Split the extension by dots
            ext_parts = parsed_dict["ext"].split(".")
            # Check for known multi-part extensions
            for i in range(len(ext_parts)):
                possible_ext = ".".join(ext_parts[i:])
                if possible_ext in Parser.known_extensions:
                    # Adjust post_numeral
                    if ext_parts[:i]:
                        parsed_dict["post_numeral"] += "." + ".".join(ext_parts[:i])
                    ext = possible_ext
                    break
            else:
                # If no known multi-part extension is found, use the last part as the extension
                if len(ext_parts) > 1:
                    parsed_dict["post_numeral"] += "." + ".".join(ext_parts[:-1])
                ext = ext_parts[-1]
        else:
            ext = ""

        # Remove trailing dot from post_numeral if present
        if parsed_dict["post_numeral"].endswith("."):
            parsed_dict["post_numeral"] = parsed_dict["post_numeral"][:-1]

        return Item(
            prefix=name,
            frame_string=parsed_dict["frame"],
            extension=ext,
            delimiter=delimiter,
            suffix=parsed_dict["post_numeral"],
            directory=Path(directory),
        )

    class SequenceDictItem(TypedDict):
        name: str
        separator: str
        suffix: str
        frames: List[str]
        extension: str
        items: List[Item]

    @staticmethod
    def filesequences_from_file_list(
        filename_list: List[str],
        directory: Optional[Path] = None,
    ) -> List[FileSequence]:

        # sequence_dict = {}
        sequence_dict: Dict[Tuple[str, str, str, str], Parser.SequenceDictItem] = {}

        for file in filename_list:
            parsed_item = Parser.item_from_filename(file, directory)
            if not parsed_item:
                continue

            # Include suffix in the key to separate sequences with different suffixes
            key = (
                parsed_item.prefix,
                parsed_item.delimiter or "",
                parsed_item.suffix or "",  # Add suffix to key
                parsed_item.extension or "",
            )

            if key not in sequence_dict:
                sequence_dict[key] = {
                    "name": parsed_item.prefix,
                    "separator": parsed_item.delimiter or "",
                    "suffix": parsed_item.suffix or "",
                    "frames": [],
                    "extension": parsed_item.extension or "",
                    "items": [],
                }

            sequence_dict[key]["items"].append(parsed_item)
            sequence_dict[key]["frames"].append(parsed_item.frame_string)

        sequence_list = []

        for seq in sequence_dict.values():
            if len(seq["items"]) < 2:
                continue

            temp_sequence = FileSequence(
                sorted(seq["items"], key=lambda i: i.frame_number)
            )

            duplicates = temp_sequence.find_duplicate_frames()

            if not duplicates:
                sequence_list.append(temp_sequence)
                continue

            padding_counts = Counter(item.padding for item in temp_sequence.items)
            nominal_padding = padding_counts.most_common(1)[0][0]

            main_sequence_items = []
            anomalous_items = defaultdict(list)
            processed_frames = set()

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
                main_sequence = FileSequence(
                    sorted(main_sequence_items, key=lambda i: i.frame_number)
                )
                sequence_list.append(main_sequence)

            for items in anomalous_items.items():
                if len(items) >= 2:
                    anomalous_sequence = FileSequence(
                        sorted(items, key=lambda i: i.frame_number)
                    )
                    sequence_list.append(anomalous_sequence)

        logging.info("Parsed %d sequences", len(sequence_list))

        return sequence_list

    @staticmethod
    def filesequences_from_directory(directory: Path) -> List[FileSequence]:
        """Scans a directory and call Parser.detect_file_sequences to return a
        list of detected sequences as FileSequence objects.

        Sequence file names are parsed into the following component form:

        <prefix><delimiter><frame><suffix><extension>

        For example:
        render.0001.grade.exr will yield:

        prefix: render
        delimiter: .
        frame: 0001
        suffix: grade
        extension: exr

        If there are missing frames, the sequence will still be parsed.

        If a sequence is detected with inconsistent frame padding, the sequence will still be returned with the inconsistent
        padding accurately represented at the Item level, however the FileSequence object will return this as a Problem
        and attempt to guess the optimum padding value when queried at the FileSequence level.

        This can happen if a sequence exceeded expected duration during generation:

        frame_998.png
        frame_999.png
        frame_1000.png

        If duplicate frames exist with different padding, the sequence will consume the one that has the most appropriate padding,
        and any files with anomalous padding will be returned in a separate sequence:

        frame_001.png
        frame_002.png
        frame_02.png
        frame_003.png
        frame_004.png
        frame_04.png
        frame_005.png

        will yield two sequences:

        [frame_001.png
        frame_002.png
        frame_003.png
        frame_004.png
        frame_005.png]

        [frame_02.png
        frame_04.png]

        Args:
            directory (str): Directory to scan
            pattern (str): Regex pattern for parsing frame-based filenames

        Returns:
            list[FileSequence]: List of Sequence objects

        """
        # if isinstance(directory, Path):
        #     directory = str(directory)

        return Parser.filesequences_from_file_list(os.listdir(str(directory)), directory)

    @staticmethod
    def filesequences_from_components_in_filename_list(
        components: Components,
        filename_list: List[str],
        directory: Optional[Path] = None,
    ) -> List[FileSequence]:
        """Matches components against a list of filenames and returns a list of
        detected sequences as FileSequence objects. If no components are
        specified, all sequences are returned. Otherwise only sequences that
        match the specified components are returned.

        Args:
            components (Components): Components to match
            filename_list (list): List of filenames
            directory (str): Directory that contains the files (optional)
            pattern (str): Regex pattern for parsing frame-based filenames (optional)

        Returns:
            list[FileSequence]: List of Sequence objects

        """

        sequences = Parser.filesequences_from_file_list(filename_list, directory)

        matches = []

        for sequence in sequences:

            match = True

            if components.prefix is not None and components.prefix != sequence.prefix:
                match = False

            if (
                components.delimiter is not None
                and components.delimiter != sequence.delimiter
            ):
                match = False

            if (
                components.padding is not None
                and components.padding != sequence.padding
            ):
                match = False

            if components.suffix is not None and components.suffix != sequence.suffix:
                match = False

            if (
                components.extension is not None
                and components.extension != sequence.extension
            ):
                match = False

            if match:
                matches.append(sequence)

        logger.info("Found %d sequences matching %s", len(matches), str(components))

        return matches

    @staticmethod
    def filesequences_from_components_in_directory(
        components: Components, directory: Path
    ) -> List[FileSequence]:
        """Matches components against a directory and returns a list of detected
        sequences as FileSequence objects. If no components are specified, all
        sequences are returned. Otherwise only sequences that match the
        specified components are returned.

        Args:
            components (Components): Components to match
            directory (str): Directory that contains the files

        Returns:
            list[FileSequence]: List of Sequence objects

        """

        sequences = Parser.filesequences_from_directory(directory)

        matches = []

        for sequence in sequences:

            match = True

            if components.prefix is not None and components.prefix != sequence.prefix:
                match = False

            if (
                components.delimiter is not None
                and components.delimiter != sequence.delimiter
            ):
                match = False

            if (
                components.padding is not None
                and components.padding != sequence.padding
            ):
                match = False

            if components.suffix is not None and components.suffix != sequence.suffix:
                match = False

            if (
                components.extension is not None
                and components.extension != sequence.extension
            ):
                match = False

            if match:
                matches.append(sequence)

        logger.info("Found %d sequences matching %s", len(matches), str(components))

        return matches

    @staticmethod
    def filesequence_from_sequence_string(
        filename: str,
        filename_list: List[str],
        directory: Optional[Path] = None,
    ) -> FileSequence | None:
        """Matches a sequence file name against a list of filenames and returns
        a detected sequence as a FileSequence object.

        Sequence filenames take the form: prefix.####.suffix.extension where the
        number of # symbols determines the padding

        Examples:

        image.####.exr
        render_###_revision.jpg
        plate_v1-#####.png

        Args:
            filename (str): Sequence file name
            filename_list (list): List of filenames
            directory (str): Directory that contains the files (optional)
            pattern (str): Regex pattern for parsing frame-based filenames (optional)

        Returns:
            FileSequence: Sequence object

        """

        sequences = Parser.filesequences_from_file_list(filename_list, directory)

        matched = []

        for sequence in sequences:

            if sequence.file_name == filename:
                matched.append(sequence)

        if len(matched) > 1:
            raise ValueError(
                f"Multiple sequences match {filename!r}: {matched!r}, should be only one"
            )

        if len(matched) == 0:
            return None

        logger.info("Found sequences matching %s", filename)

        return matched[0]

    @staticmethod
    def filesequence_from_sequence_filename_in_directory(
        filename: str,
        directory: Path,
    ) -> FileSequence | None:
        """Matches a sequence file name against a directory and returns
        a detected sequence as a FileSequence object.

        Sequence filenames take the form: prefix.####.suffix.extension where the
        number of # symbols determines the padding

        Examples:

        image.####.exr
        render_###_revision.jpg
        plate_v1-#####.png

        Args:
            filename (str): Sequence file name
            filename_list (list): List of filenames
            directory (str): Directory that contains the files (optional)
            pattern (str): Regex pattern for parsing frame-based filenames (optional)

        Returns:
            FileSequence: Sequence object

        """

        files = os.listdir(str(directory))

        return Parser.filesequence_from_sequence_string(filename, files, directory)

    @staticmethod
    def item_from_components(
        components: Components, frame: int, directory: Optional[Path] = None
    ) -> Item:
        """Converts a Components object into an Item object.

        Args:
            components (Components): Components object

        Returns:
            Item: Item object

        """

        # TODO write a test for this

        frame_string = str(frame).zfill(components.padding)

        directory = Path(directory)

        item = Item(
            prefix=components.prefix,
            frame_string=frame_string,
            extension=components.extension,
            delimiter=components.delimiter,
            suffix=components.suffix,
            directory=directory,
        )

        # if directory is not None:
        #     # item.directory = directory
        #     item.path = Path(directory) / item.filename

        # else:
        #     item.path = Path(item.filename)

        return item


class Problems(Flag):
    """Enumeration of potential issues in frame sequences using Flag for bitwise
    operations.

    Provides a way to track and combine multiple issues that might exist in a sequence,
    such as missing frames or inconsistent padding. Uses Python's Flag class to allow
    multiple problems to be represented in a single value.

    Flags:
        NONE: No problems detected
        MISSING_FRAMES: Sequence has gaps between frame numbers
        INCONSISTENT_PADDING: Frame numbers have different padding lengths
        FILE_NAME_INCLUDES_SPACES: Filenames contain spaces
        DUPLICATE_FRAME_NUMBERS_WITH_INCONSISTENT_PADDING: Same frame appears with different padding

    Methods:
        check_sequence: Analyze a FileSequence and return all detected problems

    Example:
        problems = Problems.check_sequence(sequence)
        if problems & Problems.MISSING_FRAMES:
            print("Sequence has missing frames")

    """

    NONE = 0
    # Sequence has gaps between frame numbers
    MISSING_FRAMES = auto()
    # Frame numbers have different amounts of padding
    INCONSISTENT_PADDING = auto()
    # File names contain spaces
    FILE_NAME_INCLUDES_SPACES = auto()
    # Same frame number appears with different padding
    DUPLICATE_FRAME_NUMBERS_WITH_INCONSISTENT_PADDING = auto()

    @classmethod
    def check_sequence(cls, sequence: FileSequence) -> "Problems":
        """Analyze a FileSequence and return a Problems flag with all detected
        issues.

        Args:
            sequence (FileSequence): The sequence to check

        Returns:
            Problems: A flag containing all detected problems

        """
        problems = cls.NONE

        # Check for missing frames
        if sequence.missing_frames:
            problems |= cls.MISSING_FRAMES

        # Check for inconsistent padding
        if not sequence._check_padding():
            problems |= cls.INCONSISTENT_PADDING

        # Check for spaces in filenames
        if any(" " in item.filename for item in sequence.items):
            problems |= cls.FILE_NAME_INCLUDES_SPACES

        # Check for duplicate frames with different padding
        if sequence.find_duplicate_frames():
            problems |= cls.DUPLICATE_FRAME_NUMBERS_WITH_INCONSISTENT_PADDING

        return problems


class AnomalousItemDataError(Exception):
    """Raised when unacceptable inconsistent data is found in a FileSequence."""
