import re
from .sequence import Sequence


class SequenceParser:
    def __init__(self, pattern=None):
        self.pattern = pattern or self.default_pattern()

    @staticmethod
    def default_pattern():
        return (
            r'^'
            r'(?P<name>.*?)'
            r'(?P<separator>[^a-zA-Z\d]+)?'
            r'(?P<frame>\d+)'
            r'.*?'
            r'(?:\.(?P<ext>[^\.]+))?'
            r'$'
        )

    def parse_filename(self, filename):
        """
        Parses a single filename and returns a dictionary of components.
        """
        match = re.match(self.pattern, filename)
        if not match:
            return None
        return match.groupdict()

    def find_sequences(self, file_list):
        """
        Scans the list of filenames and returns a list of Sequence instances.
        """
        sequences = {}

        for file in file_list:
            parsed = self.parse_filename(file)
            if not parsed:
                continue

            original_name = parsed['name']
            separator = parsed['separator'] or ''
            frame = int(parsed['frame'])
            extension = parsed['ext'] or ''

            cleaned_name = re.sub(r'[^a-zA-Z0-9]+$', '', original_name)
            key = (cleaned_name, separator)

            if key not in sequences:
                sequences[key] = {
                    'name': cleaned_name,
                    'separator': separator,
                    'files': [],
                    'frames': [],
                    'extension': extension,
                }

            sequences[key]['files'].append(file)
            sequences[key]['frames'].append(frame)
            # Update extension if not already set
            if not sequences[key]['extension']:
                sequences[key]['extension'] = extension

        # Create Sequence instances
        sequence_list = []
        for seq in sequences.values():
            sequence = Sequence(
                name=seq['name'],
                files=sorted(seq['files']),
                first_frame=min(seq['frames']),
                last_frame=max(seq['frames']),
                extension=seq['extension'],
            )
            sequence_list.append(sequence)

        return sequence_list

def list_sequence_files(file_list, sequence_name, extension=""):
    """
    Lists all files in the given list that match the given sequence name and extension.
    If extension is empty, it matches files without extensions.
    """
    # Prepare the extension part of the pattern
    if extension:
        if not extension.startswith('.'):
            extension = '.' + extension
        ext_pattern = re.escape(extension) + '$'
    else:
        ext_pattern = "$"
    
    # Escape the sequence name for regex
    escaped_name = re.escape(sequence_name)
    
    # Updated regex pattern to ensure no letters between sequence name and digits
    pattern = rf'^{escaped_name}[^a-zA-Z]*?(\d+).*?{ext_pattern}'
    regex = re.compile(pattern)
    
    sequence_files = []
    
    # Iterate through all files in the list
    for file in file_list:
        match = regex.match(file)
        if match:
            frame_number = int(match.group(1))  # Extract the frame number
            sequence_files.append(file)
            print(f"Matched: {file} (Frame: {frame_number})")
    
    return sequence_files

import re


def find_sequences(file_list):
    """
    Scans the list of filenames and returns a list of Sequence instances,
    each representing a sequence of files. Sequences are distinguished by
    their cleaned name and separator character(s).
    """
    sequences = {}

    # Regex pattern to match sequence files and extract components
    pattern = re.compile(
        r'^'                             # Start of string
        r'(?P<name>.*?)'                 # Non-greedy match for name
        r'(?P<separator>[^a-zA-Z\d]+)?'  # Optional separator (non-alphanumeric characters)
        r'(?P<frame>\d+)'                # Frame number (one or more digits)
        r'.*?'                           # Optional additional characters (non-greedy)
        r'(?:\.(?P<ext>[^\.]+))?'        # Optional extension without the dot
        r'$'                             # End of string
    )

    for file in file_list:
        match = pattern.match(file)
        if match:
            original_name = match.group('name')
            separator = match.group('separator') or ''
            frame = int(match.group('frame'))
            extension = match.group('ext') or ''

            # Clean the name by removing trailing non-alphanumeric characters
            cleaned_name = re.sub(r'[^a-zA-Z0-9]+$', '', original_name)

            # Use a tuple of (cleaned name, separator) as the key
            key = (cleaned_name, separator)

            if key not in sequences:
                sequences[key] = {
                    'name': cleaned_name,
                    'separator': separator,
                    'files': [],
                    'frames': [],
                    'extension': extension,
                }

            sequences[key]['files'].append(file)
            sequences[key]['frames'].append(frame)

            # Update extension if not already set and extension is not empty
            if not sequences[key]['extension'] and extension:
                sequences[key]['extension'] = extension

    # Create Sequence instances
    sequence_list = []
    for seq in sequences.values():
        name = seq['name']
        files = sorted(seq['files'])
        frames = seq['frames']
        first_frame = min(frames)
        last_frame = max(frames)
        extension = seq['extension']
        sequence = Sequence(name, files, first_frame, last_frame, extension)
        sequence_list.append(sequence)

    return sequence_list