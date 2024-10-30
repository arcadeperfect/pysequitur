from enum import Flag, auto
from pathlib import Path
import re
from dataclasses import dataclass
import os
from collections import Counter


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

    # def __init__(self, name, frame_number, extension, directory, separator=None, post_numeral=None):

    #     if not isinstance(name, str):
    #         raise ValueError("name must be a string")

    #     if not isinstance(frame_number, str):
    #         raise ValueError("frame_number must be an integer")

    #     if extension is not None and not isinstance(extension, str):
    #         raise ValueError(f"extension must be a string, got {extension}")

    #     if not isinstance(directory, pathlib.Path):
    #         raise ValueError("path must be a pathlib.Path")

    #     if separator is not None and not isinstance(separator, str):
    #         raise ValueError("separator must be a string or None")

    #     self.name = name
    #     self.frame = frame_number
    #     self.extension = extension
    #     self.separator = separator
    #     self.post_numeral = post_numeral
    #     self.path = pathlib.Path(directory, self.filename)

    # def __str__(self):

    #     string = f"name: {self.name} \n frame: {self.frame} \n extension: {self.extension} \n separator: {
    #         self.separator} \n post_numeral: {self.post_numeral} \n path: {self.path} \n"

    #     return string

    # def __repr__(self):
    #     return f"{self.name} {self.frame} {self.extension}"

    @property
    def filename(self):

        s = self.separator if self.separator else ""
        p = self.post_numeral if self.post_numeral else ""
        e = f".{self.extension}" if self.extension else ""

        return f"{self.name}{s}{self.frame_string}{p}{e}"

    @property
    def directory(self):
        return self.path.parent

    @property
    def padding(self):
        return len(self.frame_string)

    @property
    def stem(self):
        return self.path.stem

    @property
    def frame_number(self):
        return int(self.frame_string)

    @staticmethod
    def test():
        return "succerss"


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

    def _check_consistent_property(self, prop_name=None, getter=None):
        """Check if all items have the same value for a property."""
        if not self.items:
            raise ValueError("Empty sequence")
            
        if getter:
            values = [getter(item) for item in self.items]
        else:
            values = [getattr(item, prop_name) for item in self.items]
        
        first = values[0]
        if not all(v == first for v in values):
            raise AnomalousItemDataError(f"Inconsistent {prop_name or 'property'} values")
        return first



@dataclass
class file_profile:

    name: str
    frane: int
    separator: str
    post_numeral: str
    extension: str
    directory: str = None


# @dataclass
# class _sequence_profile:

#     file_profile: file_profile
#     first_frame: int
#     last_frame: int


# class Parser:

#     pattern = (
#         r'^'
#         r'(?P<name>.*?(?=(?:[^a-zA-Z\d]+)?\d{3,7}(?!.*\d{3,7})))'  # Name up to last frame number
#         r'(?P<separator>[^a-zA-Z\d]+)?'                            # Separator before frame
#         r'(?P<frame>\d{3,7})'                                      # Frame number (3-7 digits)
#         r'(?!.*\d{3,7})'                                           # Negative lookahead for more digits
#         r'(?P<post_numeral>.*?)'                                   # Non-greedy match up to extension
#         r'(?:\.(?P<ext>[^.]+(?:\.[^.]+)?))?'                       # Dot and extension (up to 2 parts)
#         r'$'
#     )

#     @staticmethod
#     def parse_filename(filename, directory="None", pattern=None):
#         """
#         Parses a single filename and returns a file_profile of components.
#         """

#         if len(Path(filename).parts) > 1:
#             raise ValueError("first argument must be a name, not a path")

#         if not pattern:
#             pattern = Parser.pattern

#         match = re.match(pattern, filename)
#         if not match:
#             return None

#         dict = match.groupdict()

#         # print(filename)
#         # print(dict)

#         if not "frame" in dict.keys():
#             raise ValueError("invalid regex, must contain 'frame' group")
#         if not "name" in dict.keys():
#             raise ValueError("invalid regex, must contain 'name' group")
#         if not "ext" in dict.keys():
#             raise ValueError("invalid regex, must contain 'ext' group")
#         if not "separator" in dict.keys():
#             raise ValueError("invalid regex, must contain 'separator' group")

#         if directory == "None":
#             directory = ""
#         path = Path(os.path.join(directory, filename))

#         if not path:
#             raise ValueError("invalid filepath")

#         ext = dict.get('ext', '')

#         return Item(dict['name'],
#                     dict['frame'],
#                     ext,
#                     path,
#                     dict['separator'],
#                     dict['post_numeral']
#                     )
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
    )

    known_extensions = {'exr.gz', 'tar.gz', 'tar.bz2', 'log.gz'}

    @staticmethod
    def parse_filename(filename, directory=None, pattern=None):
        """
        Parses a single filename and returns a file_profile of components.
        """
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

        # End of modified code

        return Item(
            dict['name'],
            dict['frame'],
            ext,
            path,
            dict['separator'],
            dict['post_numeral']
        )

    @staticmethod
    def find_sequences(filename_list, directory=None, pattern=None):
        """
        Scans the list of filenames and returns a list of Sequences.

        name: str
        frame: str
        extension: str
        path: pathlib.Path
        separator: str = None
        post_numeral: str = None

        """

        # print("\n find sequences")
        # print(filename_list)

        # return None

        sequence_dict = {}

        for file in filename_list:

            # print(file)

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

        # Create Sequence instances
        sequence_list = []
        for seq in sequence_dict.values():

            if len(seq['items']) < 2:
                continue

            sequence = FileSequence(
                sorted(seq['items'], key=lambda i: i.frame_number))

            # sequence = FileSequence(
            #     name=seq['name'],
            #     first_frame=min(seq['frames']),
            #     last_frame=max(seq['frames']),
            #     extension=seq['extension'],
            #     separator=seq['separator'],
            #     items=sorted(seq['items'], key=lambda i: i.frame),
            # )

            sequence_list.append(sequence)

        return sequence_list

        # return None



class AnomalousItemDataError(Exception):
    """
    Raised when unacceptable inconsistent data is found in a FileSequence
    """
    pass