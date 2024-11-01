from enum import Flag, auto
from pathlib import Path
import re
from dataclasses import dataclass
import os
from collections import Counter
import shutil

class Problems(Flag):
    MISSING_FRAMES = auto()
    INCONSISTENT_PADDING = auto()
    FILE_NAME_INCLUDES_SPACES = auto()
    DUPLICATE_FRAME_NUMBERS_WITH_INCONSISTENT_PADDING = auto()


@dataclass
class Item:

    name: str
    frame_string: str
    extension: str
    path: Path
    separator: str = None
    post_numeral: str = None

    def __post_init__(self):
        if any(char.isdigit() for char in self.post_numeral):
            raise ValueError("post_numeral cannot contain digits")



    @property
    def filename(self):

        s = self.separator if self.separator else ""
        p = self.post_numeral if self.post_numeral else ""
        e = f".{self.extension}" if self.extension else ""

        return f"{self.name}{s}{self.frame_string}{p}{e}"

    @property
    def directory(self):
        return str(self.path.parent)

    @property
    def padding(self):
        return len(self.frame_string)

    @property
    def stem(self):
        return self.path.stem

    @property
    def frame_number(self):
        return int(self.frame_string)
    
    # @property
    # def full_path(self):
    #     return self.path
    
    def move(self, new_directory):
        if self.path.exists():
            new_path = new_directory / self.filename
            self.path.rename(new_path)
            self.path = new_path  # Update the path attribute
        else:
            raise FileNotFoundError()

    def rename(self, new_name):

        if not self.path.exists():
            raise FileNotFoundError()
        
        if isinstance(new_name, str):
            self.name = new_name
            self.path = self.path.rename(self.path.with_name(self.filename))
            print(f"renamed {self.path} to {self.path.with_name(self.filename)}")
            return

        if isinstance(new_name, Renamer):

            if new_name.name is not None:   
                self.name = new_name.name

            if new_name.separator is not None:
                self.separator = new_name.separator

            if new_name.padding is not None:
                padding = max(new_name.padding, self._min_padding)
                self.frame_string = f"{self.frame_number:0{padding}d}"

            if new_name.post_numeral is not None:
                self.post_numeral = new_name.post_numeral

            if new_name.extension is not None:
                self.extension = new_name.extension

            self.path = self.path.rename(self.path.with_name(self.filename))
            print(f"renamed {self.path} to {self.path.with_name(self.filename)}")
            return
            
        raise ValueError("new_name must be a string or a Renamer object")

    def copy(self, new_name, new_directory=None):
        if not self.path.exists():
            raise FileNotFoundError()

        if isinstance(new_name, str):
            new_item = Item(
                name=new_name,
                frame_string=self.frame_string,
                extension=self.extension,
                path=self.path,
                separator=self.separator,
                post_numeral=self.post_numeral
            )
        elif isinstance(new_name, Renamer):
            new_item = Item(
                name=new_name.name if new_name.name is not None else self.name,
                frame_string=self.frame_string,
                extension=new_name.extension if new_name.extension is not None else self.extension,
                path=self.path,
                separator=new_name.separator if new_name.separator is not None else self.separator,
                post_numeral=new_name.post_numeral if new_name.post_numeral is not None else self.post_numeral
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
            new_item.name += "copy"
            new_path = new_path.with_name(new_item.filename)

        shutil.copy(str(self.path), str(new_path))
        new_item.path = new_path
        print(f"copied {self.path} to {new_path}")

        return new_item
        
    def delete(self):
        if self.path.exists():
            self.path.unlink()
            print(f"deleted {self.path}")
        else:
            raise FileNotFoundError()


   

    @property
    def exists(self):
        return self.path.exists()
    

    @property
    def directory(self):
        return self.path.parent

    def change_padding(self, new_padding):
        raise NotImplementedError()


    @property
    def _min_padding(self):
        return len(str(int(self.frame_string)))

@dataclass
class Renamer:

    name: str = None
    separator: str = None
    padding: int = None
    post_numeral: str = None
    extension: str = None



@dataclass
class FileSequence:

    items: list[Item]
   
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
    def name(self):
        return self._check_consistent_property(prop_name="name")

    @property
    def extension(self):
        return self._check_consistent_property(prop_name="extension")

    @property
    def separator(self):
        return self._check_consistent_property(prop_name="separator")

    @property
    def post_numeral(self):
        return self._check_consistent_property(prop_name="post_numeral")

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
        return f"{self.name}{self.separator}{padding}{self.post_numeral}.{self.extension}"
    
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
        self._check_consistent_property(prop_name="name")
        self._check_consistent_property(prop_name="extension")
        self._check_consistent_property(prop_name="separator")
        self._check_consistent_property(prop_name="post_numeral")



class Parser:
    # pattern = (
    #     r'^'
    #     r'(?P<name>.*?(?=[^a-zA-Z\d]*\d{3,7}(?!.*\d{3,7})))'  # Name up to last frame number
    #     r'(?P<separator>[^a-zA-Z\d]*)'                         # Separator before frame (optional)
    #     r'(?P<frame>\d{3,7})'                                  # Frame number (3-7 digits)
    #     r'(?!.*\d{3,7})'                                       # Negative lookahead for more digits
    #     r'(?P<post_numeral>.*?)'                               # Non-greedy match up to extension
    #     r'(?:\.(?P<ext>.*))?$'                                 # Dot and extension (everything after last dot)
    # )

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

        
        # r'^'
        # # Name including any special characters up to the single separator before frame number
        # r'(?P<name>.*?)'
        # # Single character separator before frame (optional)
        # r'(?P<separator>[^a-zA-Z\d])?'
        # # Frame number (1 or more digits)
        # r'(?P<frame>\d+)'
        # # Negative lookahead for more digits
        # r'(?!.*\d+)'
        # # Non-greedy match up to extension
        # r'(?P<post_numeral>.*?)'
        # # Dot and extension (everything after last dot)
        # r'(?:\.(?P<ext>.*))?$'
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
        """
        
        sequence_dict = {}

        for file in filename_list:

            parsed_item = Parser.parse_filename(file, directory)
            if not parsed_item:
                continue

            original_name = parsed_item.name
            separator = parsed_item.separator or ''
            frame = parsed_item.frame_string
            extension = parsed_item.extension or ''

            # Remove diving character from the end of the name
            # for example,
            # "name_" becomes "name"
            # "file." becomes "file"
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

            # Update extension if not already set (can happen with bad sequence)
            if not sequence_dict[key]['extension']:
                sequence_dict[key]['extension'] = extension


        sequence_list = []
        for seq in sequence_dict.values():

            if len(seq['items']) < 2:
                continue

            sequence = FileSequence(
                sorted(seq['items'], key=lambda i: i.frame_number))

            sequence_list.append(sequence)

        return sequence_list
    
    @staticmethod
    def scan_directory(directory, pattern=None):
        return Parser.find_sequences(os.listdir(directory), directory, pattern)

class AnomalousItemDataError(Exception):
    """
    Raised when unacceptable inconsistent data is found in a FileSequence
    """
    pass
