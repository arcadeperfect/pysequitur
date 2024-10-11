from enum import Flag, auto
import pathlib
import re

class Problems(Flag):
    MISSING_FRAMES = auto()
    INCONSISTENT_PADDING = auto()
    FILE_NAME_INCLUDES_SPACES = auto()
    DUPLICATE_FRAME_NUMBERS_WITH_INCONSISTENT_PADDING = auto()


class Item:
    def __init__(self, name, frame_number, extension, directory, separator=None):

        if not isinstance(name, str):
            raise ValueError("name must be a string")

        if not isinstance(frame_number, str):
            raise ValueError("frame_number must be an integer")

        if extension is not None and not isinstance(extension, str):
            raise ValueError(f"extension must be a string, got {extension}")

        if not isinstance(directory, pathlib.Path):
            raise ValueError("path must be a pathlib.Path")

        if separator is not None and not isinstance(separator, str):
            raise ValueError("separator must be a string or None")

        self.name = name
        self.frame = frame_number
        self.extension = extension
        self.separator = separator
        self.path = pathlib.Path(directory, self.filename)

    def __str__(self):
        return f"{self.path}"

    def __repr__(self):
        return f"{self.name} {self.frame} {self.extension}"

    @property
    def filename(self):
        if self.separator:
            return f"{self.name}{self.separator}{self.frame}.{self.extension}"
        return f"{self.name}{self.frame}.{self.extension}"

    @property
    def directory(self):
        return self.path.parent
    
    @property
    def padding(self):
        return len(self.frame)


class FileSequence:

    _pattern = (
        r'^'
        r'(?P<name>.*?)'
        r'(?P<separator>[^a-zA-Z\d]+)?'
        r'(?P<frame>\d+)'
        r'.*?'
        r'(?:\.(?P<ext>[^\.]+))?'
        r'$'
    )

    @classmethod
    def _parse_filename(cls, filename, filepath):
        """
        Parses a single filename and returns a dictionary of components.
        """
        match = re.match(cls._pattern, filename)
        if not match:
            return None
        dict = match.groupdict()

        if not "frame" in dict.keys():
            raise ValueError("invalid regex, must contain 'frame' group")
        if not "name" in dict.keys():
            raise ValueError("invalid regex, must contain 'name' group")
        if not "ext" in dict.keys():
            raise ValueError("invalid regex, must contain 'ext' group")
        if not "separator" in dict.keys():
            raise ValueError("invalid regex, must contain 'separator' group")
        
        p = pathlib.Path(filepath)

        if not p:
            raise ValueError("invalid filepath")

        return Item(dict['name'], dict['frame'], dict['ext'], p, dict['separator'])
        
    @classmethod
    def _parse_filename_list(cls, filename_list, path):
        """
        Scans the list of filenames and returns a list of Sequence instances.
        """
        sequences = {}

        for file in filename_list:
            
            parsed_item = cls._parse_filename(file, path)
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

            # print(key)
            if key not in sequences:
                sequences[key] = {
                    'name': cleaned_name,
                    'separator': separator,
                    # 'files': [],
                    'frames': [],
                    'extension': extension,
                    'items': [],
                }

            # print(sequences[key])

            # this_item = Item(name = cleaned_name, 
            #                  frame_number = frame, 
            #                  extension = extension, 
            #                  file_name = file, 
            #                  separator=separator)

            sequences[key]['items'].append(parsed_item)
            # sequences[key]['files'].append(file)
            sequences[key]['frames'].append(frame)
            # Update extension if not already set
            if not sequences[key]['extension']:
                sequences[key]['extension'] = extension

        # Create Sequence instances
        sequence_list = []
        for seq in sequences.values():

            sequence = FileSequence(
                name=seq['name'],
                # files=sorted(seq['files']),
                first_frame=min(seq['frames']),
                last_frame=max(seq['frames']),
                extension=seq['extension'],
                separator=seq['separator'],
                items=sorted(seq['items'], key=lambda i: i.frame),
            )

            sequence_list.append(sequence)

        return sequence_list

    def __init__(self, name, first_frame, last_frame, extension, items, separator=None):
        self.name = name
        # self.files = files
        self.first_frame = first_frame
        self.last_frame = last_frame
        self.extension = extension
        self.separator = separator
        self.items = items

    def __str__(self):
        return f"name: {self.name} | first_frame: {self.first_frame} | last_frame: {self.last_frame} | extension: {self.extension}"

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

    @staticmethod
    @classmethod
    def parse_filename(self, filename):
        """
        Parses a single filename and returns a dictionary of components.
        """
        match = re.match(self.pattern, filename)
        if not match:
            return None
            return match.groupdict()

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
