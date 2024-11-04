import re
import os
import shutil
from enum import Flag, auto
from typing import Dict, Tuple, List, Set
from pathlib import Path
from dataclasses import dataclass
from collections import Counter, defaultdict
from operator import attrgetter
from typing import Any


@dataclass
class Components:

    """
    Configuration class for naming operations on Items and FileSequences.

    Provides a flexible way to specify components of a filename during renaming or parsing operations. 
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

    prefix: str = None
    delimiter: str = None
    padding: int = None
    suffix: str = None
    extension: str = None


@dataclass
class Item:

    """
    Represents a single file in a frame sequence with methods for manipulation and validation.

    An Item represents one file in an image sequence, parsing and managing components like
    the prefix (base name), frame number, file extension, and any delimiters or suffixes.

    Attributes:
        prefix (str): Base name of the file before the frame number
        frame_string (str): Frame number as a string with padding
        extension (str): File extension without the dot
        path (Path): Path object representing the file location
        delimiter (str, optional): Character(s) separating prefix from frame number
        suffix (str, optional): Additional text after frame number before extension

    Example:
        For a file named "render_001.exr":
        - prefix: "render"
        - frame_string: "001"
        - extension: "exr"
        - delimiter: "_"
        - suffix: None
    """

    prefix: str
    frame_string: str
    extension: str
    path: Path
    delimiter: str = None
    suffix: str = None

    def __post_init__(self):
        if any(char.isdigit() for char in self.suffix):
            raise ValueError("suffix cannot contain digits")

        self._dirty = False

    @staticmethod
    def From_Path(path) -> "Item":
        return Parser.parse_filename(path)

    @property
    def filename(self) -> str:

        s = self.delimiter if self.delimiter else ""
        p = self.suffix if self.suffix else ""
        e = f".{self.extension}" if self.extension else ""

        return f"{self.prefix}{s}{self.frame_string}{p}{e}"

    @property
    def directory(self) -> str:
        return str(self.path.parent)

    @property
    def absolute_path(self) -> Path:
        return self.directory / self.filename

    @property
    def padding(self) -> int:
        return len(self.frame_string)

    @padding.setter
    def padding(self, value: int) -> None:
        padding = max(value, len(str(self.frame_number)))
        self.frame_string = f"{self.frame_number:0{padding}d}"
        if (self.exists):
            self.rename(Components(padding=padding))
        else:
            raise FileNotFoundError()

    @property
    def stem(self) -> str:
        return self.path.stem

    @property
    def frame_number(self) -> int:
        return int(self.frame_string)

    def set_frame_number(self, new_frame_number: int, padding: int = None) -> None:

        if new_frame_number == self.frame_number and padding == self.padding:
            return

        if new_frame_number < 0:
            raise ValueError("new_frame_number cannot be negative")

        if padding is None:
            padding = self.padding

        new_padding = max(padding, len(str(new_frame_number)))

        self.frame_string = f"{new_frame_number:0{new_padding}d}"

        self.rename()

    def move(self, new_directory: str) -> None:
        if self.path.exists():
            new_path = new_directory / self.filename
            self.path.rename(new_path)
            self.path = new_path  # Update the path attribute
        else:
            raise FileNotFoundError()

    def rename(self, new_name: str | Components = None) -> None:

        if not self.path.exists():
            raise FileNotFoundError()

        if new_name is None:
            new_name = Components()

        if isinstance(new_name, str):
            self.prefix = new_name
            self.path = self.path.rename(self.path.with_name(self.filename))
            return

        if isinstance(new_name, Components):

            if new_name.prefix is not None:
                self.prefix = new_name.prefix

            if new_name.delimiter is not None:
                self.delimiter = new_name.delimiter

            if new_name.padding is not None:
                padding = max(new_name.padding, self._min_padding)
                self.frame_string = f"{self.frame_number:0{padding}d}"

            if new_name.suffix is not None:
                self.suffix = new_name.suffix

            if new_name.extension is not None:
                self.extension = new_name.extension

            self.path = self.path.rename(self.path.with_name(self.filename))

            return

        raise ValueError("new_name must be a string or a Renamer object")

    def copy(self, new_name: str, new_directory: str = None) -> "Item":
        if not self.path.exists():
            raise FileNotFoundError()

        if isinstance(new_name, str):
            new_item = Item(
                prefix=new_name,
                frame_string=self.frame_string,
                extension=self.extension,
                path=self.path,
                delimiter=self.delimiter,
                suffix=self.suffix
            )
        elif isinstance(new_name, Components):
            new_item = Item(
                prefix=new_name.prefix if new_name.prefix is not None else self.prefix,
                frame_string=self.frame_string,
                extension=new_name.extension if new_name.extension is not None else self.extension,
                path=self.path,
                delimiter=new_name.delimiter if new_name.delimiter is not None else self.delimiter,
                suffix=new_name.suffix if new_name.suffix is not None else self.suffix
            )
            if new_name.padding is not None:
                padding = max(new_name.padding, self._min_padding)
                new_item.frame_string = f"{self.frame_number:0{padding}d}"
        else:
            raise ValueError("new_name must be a string or a Renamer object")

        if new_directory is not None:
            new_path = new_directory / new_item.filename
        else:
            new_path = self.path.with_name(new_item.filename)

        if new_path == self.path:
            new_item.prefix += "copy"
            new_path = new_path.with_name(new_item.filename)

        shutil.copy(str(self.path), str(new_path))
        new_item.path = new_path

        return new_item

    def delete(self) -> None:
        if self.path.exists():
            self.path.unlink()
        else:
            raise FileNotFoundError()

    @property
    def exists(self) -> bool:
        return self.path.exists()

    @property
    def directory(self) -> Path:
        return self.path.parent

    @property
    def _min_padding(self) -> int:
        return len(str(int(self.frame_string)))

    def _check_path(self) -> bool:
        """
        Checks if the path computed from the components matches the path object
        """

        if not self.path.exists():
            raise FileNotFoundError()

        if not self.absolute_path == str(self.path):
            dirty = True
            return False

        return True


@dataclass
class FileSequence:

    """
    Manages a collection of related Items that form an image sequence.

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
    def existing_frames(self) -> list[int]:
        return [(item.frame_number) for item in self.items]

    @property
    def missing_frames(self) -> list[int]:
        frames = self.existing_frames
        return [frame for frame in range(self.first_frame, self.last_frame) if frame not in frames]

    @property
    def frame_count(self) -> int:
        return self.last_frame - self.first_frame

    @property
    def first_frame(self) -> int:
        return min(self.items, key=lambda item: item.frame_number).frame_number

    @property
    def last_frame(self) -> int:
        return max(self.items, key=lambda item: item.frame_number).frame_number

    @property
    def prefix(self) -> str:
        return self._check_consistent_property(prop_name="prefix")

    @property
    def extension(self) -> str:
        return self._check_consistent_property(prop_name="extension")

    @property
    def delimiter(self) -> str:
        return self._check_consistent_property(prop_name="delimiter")

    @property
    def suffix(self) -> str:
        return self._check_consistent_property(prop_name="suffix")

    @property
    def directory(self) -> str:
        return self._check_consistent_property(prop_name="directory")

    @property
    def missing_frames(self) -> list[int]:
        return [item.frame_number for item in self.items]

    @property
    def missing_frames(self) -> set:
        return set(range(self.first_frame, self.last_frame + 1)) - set(self.existing_frames)

    @property
    def frame_count(self) -> int:
        return self.last_frame + 1 - self.first_frame

    @property
    def padding(self) -> int:
        if not self.items:
            return None
        padding_counts = Counter(item.padding for item in self.items)
        return padding_counts.most_common(1)[0][0]

    @property
    def file_name(self) -> str:
        padding = '#' * self.padding
        return f"{self.prefix}{self.delimiter}{padding}{self.suffix}.{self.extension}"

    @property
    def absolute_file_name(self) -> str:
        return os.path.join(self.directory, self.file_name)

    @property
    def problems(self) -> "Problems":
        return Problems.check_sequence(self)

    @classmethod
    def fromFileList(cls, filename_list: List[str], directory: str = None, pattern: str = None) -> 'FileSequence':
        return cls(Parser.detect_file_sequences(filename_list, directory, pattern))

    @classmethod
    def fromDirectory(cls, directory: str, pattern: str = None) -> 'FileSequence':
        return cls(Parser.detect_file_sequences(directory, pattern=pattern))

    def rename(self, new_name: str) -> None:

        self._validate()

        for item in self.items:
            item.rename(new_name)

    def move(self, new_directory: str) -> None:
        for item in self.items:
            item.move(new_directory)

    def delete(self) -> None:
        for item in self.items:
            item.delete()

    def copy(self, new_name: str, new_directory: str = None) -> 'FileSequence':
        self._validate()

        new_items = []
        for item in self.items:
            new_item = item.copy(new_name, new_directory)
            new_items.append(new_item)

        new_sequence = FileSequence(new_items)
        return new_sequence

    def offset_frames(self, offset: int, padding: int = None) -> None:

        if offset == 0:
            return

        if self.first_frame + offset < 0:
            raise ValueError("offset would yield negative frame numbers")

        if padding is None:
            padding = self.padding

        padding = max(padding, len(str(self.last_frame + offset)))

        for item in sorted(self.items, key=attrgetter('frame_number'), reverse=offset > 0):

            target = item.frame_number + offset

            if any(item.frame_number == target for item in self.items):
                raise ValueError(f"Frame {target} already exists")

            item.set_frame_number(item.frame_number + offset, padding)

    def set_padding(self, padding=0) -> None:

        padding = max(padding, len(str(self.last_frame)))

        for item in self.items:
            item.padding = padding

    def find_duplicate_frames(self) -> Dict[int, Tuple[Item, ...]]:
        """
        Identifies frames that appear multiple times with different padding.
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
            frame: items for frame, items in frame_groups.items()
            if len(items) > 1
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
                    str(x)
                )
            )
            result[frame_number] = tuple(sorted_items)

        return result

    def _check_consistent_property(self, prop_name: str) -> Any:
        """Check if all items have the same value for a property."""
        if not self.items:
            raise ValueError("Empty sequence")

        values = [getattr(item, prop_name) for item in self.items]

        first = values[0]
        if not all(v == first for v in values):
            raise AnomalousItemDataError(f"Inconsistent {prop_name} values")
        return first

    def _validate(self) -> None:
        self._check_consistent_property(prop_name="prefix")
        self._check_consistent_property(prop_name="extension")
        self._check_consistent_property(prop_name="delimiter")
        self._check_consistent_property(prop_name="suffix")
        self._check_consistent_property(prop_name="directory")

    def _check_padding(self) -> bool:
        if not all(item.padding == self.padding for item in self.items):
            return False
        return True


class Parser:

    """
    Static utility class for parsing filenames and discovering sequences.

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
        r'^'
        # Name up to last frame number
        r'(?P<name>.*?(?=[^a-zA-Z\d]*\d+(?!.*\d+)))'
        # Separator before frame (optional)
        r'(?P<separator>[^a-zA-Z\d]*)'
        # Frame number (1 or more digits)
        r'(?P<frame>\d+)'
        # Negative lookahead for more digits
        r'(?!.*\d+)'
        # Non-greedy match up to extension
        r'(?P<post_numeral>.*?)'
        # Dot and extension (everything after last dot)
        r'(?:\.(?P<ext>.*))?$'
    )

    known_extensions = {'tar.gz', 'tar.bz2', 'log.gz'}

    @staticmethod
    def parse_filename(filename: str,
                       directory: str = None,
                       pattern: str = None) -> Item:
        """
        Parses a single filename and returns an Item object.
        """

        if isinstance(filename, Path):
            directory = filename.parent
            filename = filename.name

        if len(Path(filename).parts) > 1:
            raise ValueError("first argument must be a name, not a path")

        if not pattern:
            pattern = Parser.pattern

        match = re.match(pattern, filename)
        if not match:
            return None

        dict = match.groupdict()

        # Set default values if keys are missing
        dict.setdefault('frame', '')
        dict.setdefault('name', '')
        dict.setdefault('ext', '')
        dict.setdefault('separator', '')
        dict.setdefault('post_numeral', '')

        name = dict['name']
        separator = dict['separator']

        if len(separator) > 1:
            name += separator[0:-1]
            separator = separator[-1]

        if directory == None:
            directory = ""
        path = Path(os.path.join(directory, filename))

        if not path:
            raise ValueError("invalid filepath")

        # Start of modified code
        ext = dict.get('ext', '')

        if dict['ext']:
            # Split the extension by dots
            ext_parts = dict['ext'].split('.')
            # Check for known multi-part extensions
            for i in range(len(ext_parts)):
                possible_ext = '.'.join(ext_parts[i:])
                if possible_ext in Parser.known_extensions:
                    # Adjust post_numeral
                    if ext_parts[:i]:
                        dict['post_numeral'] += '.' + '.'.join(ext_parts[:i])
                    ext = possible_ext
                    break
            else:
                # If no known multi-part extension is found, use the last part as the extension
                if len(ext_parts) > 1:
                    dict['post_numeral'] += '.' + '.'.join(ext_parts[:-1])
                ext = ext_parts[-1]
        else:
            ext = ''

        # Remove trailing dot from post_numeral if present
        if dict['post_numeral'].endswith('.'):
            dict['post_numeral'] = dict['post_numeral'][:-1]

        return Item(
            name,
            dict['frame'],
            ext,
            path,
            separator,
            dict['post_numeral']
        )

    @staticmethod
    def detect_file_sequences(filename_list: List[str],
                              directory: str = None,
                              pattern: str = None) -> List[FileSequence]:
        """
        Iterates through a list of filenames and returns a list of detected sequences as FileSequence objects.

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
            filename_list (list): List of filenames
            directory (str): Directory that contains the files
            pattern (str): Regex pattern for parsing frame-based filenames

        Returns:
            list[FileSequence]: List of Sequence objects
        """

        sequence_dict = {}

        for file in filename_list:
            parsed_item = Parser.parse_filename(file, directory)
            if not parsed_item:
                continue

            # Include suffix in the key to separate sequences with different suffixes
            key = (parsed_item.prefix, 
                  parsed_item.delimiter or '', 
                  parsed_item.suffix or '',  # Add suffix to key
                  parsed_item.extension or '')

            if key not in sequence_dict:
                sequence_dict[key] = {
                    'name': parsed_item.prefix,
                    'separator': parsed_item.delimiter or '',
                    'suffix': parsed_item.suffix or '',
                    'frames': [],
                    'extension': parsed_item.extension or '',
                    'items': [],
                }

            sequence_dict[key]['items'].append(parsed_item)
            sequence_dict[key]['frames'].append(parsed_item.frame_string)

        sequence_list = []

        for seq in sequence_dict.values():
            if len(seq['items']) < 2:
                continue

            temp_sequence = FileSequence(
                sorted(seq['items'], key=lambda i: i.frame_number))

            duplicates = temp_sequence.find_duplicate_frames()

            if not duplicates:
                sequence_list.append(temp_sequence)
                continue

            padding_counts = Counter(
                item.padding for item in temp_sequence.items)
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
                    sorted(main_sequence_items, key=lambda i: i.frame_number))
                sequence_list.append(main_sequence)

            for padding, items in anomalous_items.items():
                if len(items) >= 2:
                    anomalous_sequence = FileSequence(
                        sorted(items, key=lambda i: i.frame_number))
                    sequence_list.append(anomalous_sequence)

        return sequence_list

        # sequence_dict = {}

        # for file in filename_list:
        #     parsed_item = Parser.parse_filename(file, directory)
        #     if not parsed_item:
        #         continue

        #     original_name = parsed_item.prefix
        #     separator = parsed_item.delimiter or ''
        #     frame = parsed_item.frame_string
        #     extension = parsed_item.extension or ''

        #     # Remove dividing character from the end of the name
        #     cleaned_name = re.sub(r'[^a-zA-Z0-9]+$', '', original_name)
        #     key = (cleaned_name, separator, extension)

        #     if key not in sequence_dict:
        #         sequence_dict[key] = {
        #             'name': cleaned_name,
        #             'separator': separator,
        #             'frames': [],
        #             'extension': extension,
        #             'items': [],
        #         }

        #     sequence_dict[key]['items'].append(parsed_item)
        #     sequence_dict[key]['frames'].append(frame)

        #     if not sequence_dict[key]['extension']:
        #         sequence_dict[key]['extension'] = extension

        # sequence_list = []

        # for seq in sequence_dict.values():
        #     if len(seq['items']) < 2:
        #         continue

        #     temp_sequence = FileSequence(
        #         sorted(seq['items'], key=lambda i: i.frame_number))

        #     duplicates = temp_sequence.find_duplicate_frames()

        #     if not duplicates:
        #         sequence_list.append(temp_sequence)
        #         continue

        #     padding_counts = Counter(
        #         item.padding for item in temp_sequence.items)
        #     nominal_padding = padding_counts.most_common(1)[0][0]

        #     main_sequence_items = []
        #     anomalous_items = defaultdict(list)
        #     processed_frames = set()

        #     for item in temp_sequence.items:
        #         if item.frame_number in processed_frames:
        #             continue

        #         if item.frame_number in duplicates:
        #             duplicate_items = duplicates[item.frame_number]
        #             for dup_item in duplicate_items:
        #                 if dup_item.padding == nominal_padding:
        #                     main_sequence_items.append(dup_item)
        #                 else:
        #                     anomalous_items[dup_item.padding].append(dup_item)
        #         else:
        #             main_sequence_items.append(item)

        #         processed_frames.add(item.frame_number)

        #     if len(main_sequence_items) >= 2:
        #         main_sequence = FileSequence(
        #             sorted(main_sequence_items, key=lambda i: i.frame_number))
        #         sequence_list.append(main_sequence)
        #     for padding, items in anomalous_items.items():
        #         if len(items) >= 2:
        #             anomalous_sequence = FileSequence(
        #                 sorted(items, key=lambda i: i.frame_number))
        #             sequence_list.append(anomalous_sequence)

        # return sequence_list

    @staticmethod
    def scan_directory(directory: str,
                       pattern: str = None) -> List[FileSequence]:
        """
        Scans a directory and call Parser.detect_file_sequences to return a list of detected sequences as FileSequence objects.

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
        return Parser.detect_file_sequences(os.listdir(directory), directory, pattern)

    @staticmethod
    def match_components(components: Components,
                         filename_list: List[str],
                         directory: str = None,
                         pattern: str = None) -> List[FileSequence]:
        """
        Matches components against a list of filenames and returns a list of detected sequences as FileSequence objects.
        If no components are specified, all sequences are returned.
        Otherwise only sequences that match the specified components are returned.

        Args:
            components (Components): Components to match
            filename_list (list): List of filenames
            directory (str): Directory that contains the files (optional)
            pattern (str): Regex pattern for parsing frame-based filenames (optional)

        Returns:
            list[FileSequence]: List of Sequence objects
        """

        sequences = Parser.detect_file_sequences(
            filename_list, directory, pattern)

        matches = []

        for sequence in sequences:

            match = True

            if components.prefix is not None and components.prefix != sequence.prefix:
                match = False

            if components.delimiter is not None and components.delimiter != sequence.delimiter:
                match = False

            if components.padding is not None and components.padding != sequence.padding:
                match = False

            if components.suffix is not None and components.suffix != sequence.suffix:
                match = False

            if components.extension is not None and components.extension != sequence.extension:
                match = False

            if match:
                matches.append(sequence)

        return matches

    @staticmethod
    def match_components_in_directory(components: Components,
                                      directory: str,
                                      pattern: str = None) -> List[FileSequence]:
        """
        Matches components against a directory and returns a list of detected sequences as FileSequence objects.
        If no components are specified, all sequences are returned.
        Otherwise only sequences that match the specified components are returned.

        Args:
            components (Components): Components to match
            directory (str): Directory that contains the files
            pattern (str): Regex pattern for parsing frame-based filenames

        Returns:
            list[FileSequence]: List of Sequence objects
        """

        sequences = Parser.scan_directory(directory, pattern)

        matches = []

        for sequence in sequences:

            match = True

            if components.prefix is not None and components.prefix != sequence.prefix:
                match = False

            if components.delimiter is not None and components.delimiter != sequence.delimiter:
                match = False

            if components.padding is not None and components.padding != sequence.padding:
                match = False

            if components.suffix is not None and components.suffix != sequence.suffix:
                match = False

            if components.extension is not None and components.extension != sequence.extension:
                match = False

            if match:
                matches.append(sequence)

        return matches

    @staticmethod
    def match_sequence_file_name(filename: str, filename_list: List[str], directory: str = None, pattern: str = None) -> FileSequence:
        """
        Matches a sequence file name against a list of filenames and returns a detected sequence as a FileSequence object.

        Sequence filenames take the form: prefix.####.suffix.extension where the number of # symbols determines the padding

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

        sequences = Parser.detect_file_sequences(
            filename_list, directory, pattern)

        matched = []

        for sequence in sequences:

            if sequence.filename == filename:
                matched.append(sequence)

        return matched



class Problems(Flag):
    """
    Enumeration of potential issues in frame sequences using Flag for bitwise operations.

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
    def check_sequence(cls, sequence) -> 'Problems':
        """
        Analyze a FileSequence and return a Problems flag with all detected issues.

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
        if any(' ' in item.filename for item in sequence.items):
            problems |= cls.FILE_NAME_INCLUDES_SPACES

        # Check for duplicate frames with different padding
        if sequence.find_duplicate_frames():
            problems |= cls.DUPLICATE_FRAME_NUMBERS_WITH_INCONSISTENT_PADDING

        return problems


class AnomalousItemDataError(Exception):
    """
    Raised when unacceptable inconsistent data is found in a FileSequence
    """
    pass
