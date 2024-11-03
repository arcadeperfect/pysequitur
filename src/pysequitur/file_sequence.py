import re
import os
import shutil
from enum import Flag, auto
from typing import Dict, Tuple, List, Set
from pathlib import Path
from dataclasses import dataclass
from collections import Counter, defaultdict
from operator import attrgetter


class Problems(Flag):
    MISSING_FRAMES = auto()
    INCONSISTENT_PADDING = auto()
    FILE_NAME_INCLUDES_SPACES = auto()
    DUPLICATE_FRAME_NUMBERS_WITH_INCONSISTENT_PADDING = auto()


@dataclass
class Item:

    prefix: str
    frame_string: str
    extension: str
    path: Path
    delimiter: str = None
    suffix: str = None

    def __post_init__(self):
        if any(char.isdigit() for char in self.suffix):
            raise ValueError("post_numeral cannot contain digits")
        
        self._dirty = False

    @staticmethod
    def From_Path(path):
        return Parser.parse_filename(path)


    @property
    def filename(self):

        s = self.delimiter if self.delimiter else ""
        p = self.suffix if self.suffix else ""
        e = f".{self.extension}" if self.extension else ""

        return f"{self.prefix}{s}{self.frame_string}{p}{e}"

    @property
    def directory(self):
        return str(self.path.parent)

    @property
    def absolute_path(self):
        return self.directory / self.filename
        
    @property
    def padding(self):
        return len(self.frame_string)

    @padding.setter
    def padding(self, value):
        padding = max(value, len(str(self.frame_number)))
        self.frame_string = f"{self.frame_number:0{padding}d}"
        if(self.exists):
            self.rename(Renamer(padding=padding))
        else:
            raise FileNotFoundError()

    @property
    def stem(self):
        return self.path.stem

    @property
    def frame_number(self):
        return int(self.frame_string)

    
    def set_frame_number(self, new_frame_number, padding = None):

            if new_frame_number == self.frame_number and padding == self.padding:
                return

            if new_frame_number < 0:
                raise ValueError("new_frame_number cannot be negative")

            if padding is None:
                padding = self.padding
            
            new_padding = max(padding, len(str(new_frame_number)))

            self.frame_string = f"{new_frame_number:0{new_padding}d}"

            self.rename()


    def move(self, new_directory):
        if self.path.exists():
            new_path = new_directory / self.filename
            self.path.rename(new_path)
            self.path = new_path  # Update the path attribute
        else:
            raise FileNotFoundError()

    def rename(self, new_name = None):

        if not self.path.exists():
            raise FileNotFoundError()
        
        if new_name is None:
            new_name = Renamer()

        if isinstance(new_name, str):
            self.prefix = new_name
            self.path = self.path.rename(self.path.with_name(self.filename))
            return

        if isinstance(new_name, Renamer):

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

    def copy(self, new_name, new_directory=None):
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
        elif isinstance(new_name, Renamer):
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
        
    def delete(self):
        if self.path.exists():
            self.path.unlink()
        else:
            raise FileNotFoundError()

    @property
    def exists(self):
        return self.path.exists()
    
    @property
    def directory(self):
        return self.path.parent
    
  

    @property
    def _min_padding(self):
        return len(str(int(self.frame_string)))
    
    def _check_path(self):

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
class Renamer:

    prefix: str = None
    delimiter: str = None
    padding: int = None
    suffix: str = None
    extension: str = None

@dataclass
class FileSequence:

    items: list[Item]
   
    def __str__(self) -> str:
        result = ""
        for item in self.items:
            result += str(item) + "\n"

        return result

    @property
    def existing_frames(self):
        return [(item.frame_number) for item in self.items]

    @property
    def missing_frames(self):
        frames = self.existing_frames
        return [frame for frame in range(self.first_frame, self.last_frame) if frame not in frames]

    @property
    def frame_count(self):
        return self.last_frame - self.first_frame

    @property
    def healthy(self):
        raise NotImplementedError()

    @property
    def first_frame(self):
        return min(self.items, key=lambda item: item.frame_number).frame_number

    @property
    def last_frame(self):
        return max(self.items, key=lambda item: item.frame_number).frame_number

    @property
    def prefix(self):
        return self._check_consistent_property(prop_name="prefix")

    @property
    def extension(self):
        return self._check_consistent_property(prop_name="extension")

    @property
    def delimiter(self):
        return self._check_consistent_property(prop_name="delimiter")

    @property
    def suffix(self):
        return self._check_consistent_property(prop_name="suffix")

    @property
    def directory(self):
        return self._check_consistent_property(prop_name="directory")

    @property
    def missing_frames(self):
        return [item.frame_number for item in self.items]

    @property
    def missing_frames(self):
        return set(range(self.first_frame, self.last_frame + 1)) - set(self.existing_frames)

    @property
    def frame_count(self):
        return self.last_frame + 1 - self.first_frame

    @property
    def padding(self):
        if not self.items:
            return None 
        padding_counts = Counter(item.padding for item in self.items)
        return padding_counts.most_common(1)[0][0]
    
    @property
    def file_name(self):
        padding = '#' * self.padding
        return f"{self.prefix}{self.delimiter}{padding}{self.suffix}.{self.extension}"
    
    @property
    def absolute_file_name(self):
        return os.path.join(self.directory, self.file_name)
        
    def rename(self, new_name):

        self._validate()

        for item in self.items:
            item.rename(new_name)
    
    def move(self, new_directory):
        for item in self.items:
            item.move(new_directory)

    def delete(self):
        for item in self.items:
            item.delete()

    def copy(self, new_name, new_directory=None):
        self._validate()

        new_items = []
        for item in self.items:
            new_item = item.copy(new_name, new_directory)
            new_items.append(new_item)

        new_sequence = FileSequence(new_items)
        return new_sequence

    def offset_frames(self, offset, padding = None):
        
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

    def set_padding(self, padding = 0):
        
        padding = max(padding, len(str(self.last_frame)))         

        for item in self.items:
            item.padding = padding


    # def _check_duplicate_frames(self):
    #     duplicates = {}
    #     frames = []

    #     for item in self.items:
    #         if item.frame_number in frames:
    #             duplicates[item.frame_string] = item
    #         else:
    #             frames.append(item.frame_number)

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

    def _check_consistent_property(self, prop_name):
        """Check if all items have the same value for a property."""
        if not self.items:
            raise ValueError("Empty sequence")
            
        values = [getattr(item, prop_name) for item in self.items]
        
        first = values[0]
        if not all(v == first for v in values):
            raise AnomalousItemDataError(f"Inconsistent {prop_name} values")
        return first
    
    def _validate(self):
        self._check_consistent_property(prop_name="prefix")
        self._check_consistent_property(prop_name="extension")
        self._check_consistent_property(prop_name="delimiter")
        self._check_consistent_property(prop_name="suffix")
        self._check_consistent_property(prop_name="directory")

    def _check_padding(self):
        if not all(item.padding == self.padding for item in self.items):
            return False
        return True

class Parser:
   
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

    known_extensions = {'exr.gz', 'tar.gz', 'tar.bz2', 'log.gz'}

    @staticmethod
    def parse_filename(filename, directory=None, pattern=None):
        """
        Parses a single filename and returns a file_profile of components.
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
    def find_sequences(filename_list, directory=None, pattern=None):
        """
        Scans the list of filenames and returns a list of Sequences.
        Groups files by name/separator/extension, then subdivides groups with duplicate frames
        into separate sequences based on padding.
        """
        sequence_dict = {}

        for file in filename_list:
            parsed_item = Parser.parse_filename(file, directory)
            if not parsed_item:
                continue

            original_name = parsed_item.prefix
            separator = parsed_item.delimiter or ''
            frame = parsed_item.frame_string
            extension = parsed_item.extension or ''

            # Remove dividing character from the end of the name
            cleaned_name = re.sub(r'[^a-zA-Z0-9]+$', '', original_name)
            key = (cleaned_name, separator, extension)

            if key not in sequence_dict:
                sequence_dict[key] = {
                    'name': cleaned_name,
                    'separator': separator,
                    'frames': [],
                    'extension': extension,
                    'items': [],
                }

            sequence_dict[key]['items'].append(parsed_item)
            sequence_dict[key]['frames'].append(frame)

            if not sequence_dict[key]['extension']:
                sequence_dict[key]['extension'] = extension

        sequence_list = []
        for seq in sequence_dict.values():
            if len(seq['items']) < 2:
                continue

            # Create initial sequence with all items
            temp_sequence = FileSequence(sorted(seq['items'], key=lambda i: i.frame_number))
            
            # Check for duplicate frames
            duplicates = temp_sequence.find_duplicate_frames()
            
            if not duplicates:
                # If no duplicates, add the sequence as is
                sequence_list.append(temp_sequence)
                continue
                
            # Get the nominal padding value (most common padding)
            padding_counts = Counter(item.padding for item in temp_sequence.items)
            nominal_padding = padding_counts.most_common(1)[0][0]
            
            # Separate items into main sequence (nominal padding) and anomalous sequences
            main_sequence_items = []
            anomalous_items = defaultdict(list)  # Group anomalous items by their padding
            
            # Process each frame number
            processed_frames = set()
            for item in temp_sequence.items:
                if item.frame_number in processed_frames:
                    continue
                    
                if item.frame_number in duplicates:
                    # For duplicate frames, distribute items based on padding
                    duplicate_items = duplicates[item.frame_number]
                    for dup_item in duplicate_items:
                        if dup_item.padding == nominal_padding:
                            main_sequence_items.append(dup_item)
                        else:
                            anomalous_items[dup_item.padding].append(dup_item)
                else:
                    # For non-duplicate frames, add to main sequence
                    main_sequence_items.append(item)
                    
                processed_frames.add(item.frame_number)
                
            # Create and add main sequence if it has at least 2 items
            if len(main_sequence_items) >= 2:
                main_sequence = FileSequence(sorted(main_sequence_items, key=lambda i: i.frame_number))
                sequence_list.append(main_sequence)
                
            # Create and add anomalous sequences if they have at least 2 items
            for padding, items in anomalous_items.items():
                if len(items) >= 2:
                    anomalous_sequence = FileSequence(sorted(items, key=lambda i: i.frame_number))
                    sequence_list.append(anomalous_sequence)

        return sequence_list


    @staticmethod
    def scan_directory(directory, pattern=None):
        return Parser.find_sequences(os.listdir(directory), directory, pattern)


class AnomalousItemDataError(Exception):
    """
    Raised when unacceptable inconsistent data is found in a FileSequence
    """
    pass