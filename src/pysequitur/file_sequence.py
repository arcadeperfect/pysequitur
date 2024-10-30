from enum import Flag, auto
from pathlib import Path
import re
from dataclasses import dataclass
import os


class Problems(Flag):
    MISSING_FRAMES = auto()
    INCONSISTENT_PADDING = auto()
    FILE_NAME_INCLUDES_SPACES = auto()
    DUPLICATE_FRAME_NUMBERS_WITH_INCONSISTENT_PADDING = auto()


@dataclass
class Item:

    name: str
    frame: str
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

        return f"{self.name}{s}{self.frame}{p}{e}"

    @property
    def directory(self):
        return self.path.parent

    @property
    def padding(self):
        return len(self.frame)

    @property
    def stem(self):
        return self.path.stem


@dataclass
class FileSequence:

    # name: str
    # first_frame: int
    # last_frame: int
    # extension: str
    items: list[Item]
    # separator: str = None
    # post_numeral: str = None

    # _pattern = (
    #     r'^'
    #     r'(?P<name>.*?)'
    #     r'(?P<separator>[^a-zA-Z\d]+)?'
    #     r'(?P<frame>\d+)'
    #     r'(?P<post_numeral>[^a-zA-Z\d]?.*?)'
    #     r'(?:\.(?P<ext>(?:[^\.]+\.)*[^\.]+))?'  # Modified to capture multiple extensions
    #     r'$'
    # )

    # def __init__(self, name, first_frame, last_frame, extension, items, separator=None):
    #     self.name = name
    #     # self.files = files
    #     self.first_frame = first_frame
    #     self.last_frame = last_frame
    #     self.extension = extension
    #     self.separator = separator
    #     self.items = items

    def __str__(self):
        return f"name: {self.name} \n first_frame: {self.first_frame} \n last_frame: {self.last_frame} \n extension: {self.extension}"

    def __eq__(self, other):

        if not isinstance(other, FileSequence):
            return False

        equal = True

        if self.name != other.name:
            equal = False

        if self.first_frame != other.first_frame:
            equal = False

        if self.last_frame != other.last_frame:
            equal = False

        if self.extension != other.extension:
            equal = False

        if self.files != other.files:
            equal = False

        return equal

    @property
    def existing_frames(self):
        frames = [item.frame_number for item in self.items]

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
        return min(self.items, key=lambda item: item.frame).frame

    @property
    def last_frame(self):
        return max(self.items, key=lambda item: item.frame).frame

    @property
    def name(self):
        return self.items[0].name

    @property
    def extension(self):
        return self.items[0].extension

    @property
    def separator(self):
        return self.items[0].separator

    @property
    def post_numeral(self):
        return self.items[0].post_numeral

    @property
    def missing_frames(self):
        return [item.frame for item in self.items]

    @property
    def missing_frames(self):
        return set(range(self.first_frame, self.last_frame + 1)) - set(self.existing_frames)

    @property
    def frame_count(self):
        return self.last_frame - self.first_frame


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
    pattern = (
        r'^'
        r'(?P<name>.*?(?=[^a-zA-Z\d]*\d{3,7}(?!.*\d{3,7})))'  # Name up to last frame number
        r'(?P<separator>[^a-zA-Z\d]*)'                         # Separator before frame (optional)
        r'(?P<frame>\d{3,7})'                                  # Frame number (3-7 digits)
        r'(?!.*\d{3,7})'                                       # Negative lookahead for more digits
        r'(?P<post_numeral>.*?)'                               # Non-greedy match up to extension
        r'(?:\.(?P<ext>.*))?$'                                 # Dot and extension (everything after last dot)
    )

    known_extensions = {'exr.gz', 'tar.gz', 'tar.bz2', 'log.gz'}

    @staticmethod
    def parse_filename(filename, directory="None", pattern=None):
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

        if directory == "None":
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
        sequences = {}

        for file in filename_list:

            parsed_item = Parser.parse_filename(file, directory)
            if not parsed_item:
                continue

            original_name = parsed_item.name
            separator = parsed_item.separator or ''
            frame = parsed_item.frame
            extension = parsed_item.extension or ''

            # Remove diving character from the end of the name
            # for example,
            # "name_" becomes "name"
            # "file." becomes "file"
            cleaned_name = re.sub(r'[^a-zA-Z0-9]+$', '', original_name)
            key = (cleaned_name, separator, extension)

            if key not in sequences:
                sequences[key] = {
                    'name': cleaned_name,
                    'separator': separator,
                    'frames': [],
                    'extension': extension,
                    'items': [],
                }

            sequences[key]['items'].append(parsed_item)
            sequences[key]['frames'].append(frame)
            # Update extension if not already set (can happen with bad sequence)
            if not sequences[key]['extension']:
                sequences[key]['extension'] = extension

        # Create Sequence instances
        sequence_list = []
        for seq in sequences.values():

            sequence = FileSequence(
                name=seq['name'],
                first_frame=min(seq['frames']),
                last_frame=max(seq['frames']),
                extension=seq['extension'],
                separator=seq['separator'],
                items=sorted(seq['items'], key=lambda i: i.frame),
            )

            sequence_list.append(sequence)

        return sequence_list
