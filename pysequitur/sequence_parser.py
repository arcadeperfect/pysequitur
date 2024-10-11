import re
from .file_sequence import FileSequence, Item


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
                    'files': [],
                    'frames': [],
                    'extension': extension,
                    'items': [],
                }

            # print(sequences[key])

            this_item = Item(name = cleaned_name, 
                             frame_number = frame, 
                             extension = extension, 
                             file_name = file, 
                             separator=separator)

            sequences[key]['items'].append(this_item)
            sequences[key]['files'].append(file)
            sequences[key]['frames'].append(frame)
            # Update extension if not already set
            if not sequences[key]['extension']:
                sequences[key]['extension'] = extension

        # Create Sequence instances
        sequence_list = []
        for seq in sequences.values():

            sequence = FileSequence(
                name=seq['name'],
                files=sorted(seq['files']),
                first_frame=min(seq['frames']),
                last_frame=max(seq['frames']),
                extension=seq['extension'],
                separator=seq['separator'],
                items=sorted(seq['items'], key=lambda i: i.frame_number),
            )

            sequence_list.append(sequence)

        return sequence_list

    # def get_sequence(self, file_list, sequence_name, extension=None):

   
    def list_sequence_files(self, file_list, sequence_name, extension=""):
        """
        Lists all files in the given list that match the given sequence name and extension.
        If extension is empty, it matches files without extensions.
        """
        if extension:
            if not extension.startswith('.'):
                extension = '.' + extension
            ext_pattern = re.escape(extension) + '$'
        else:
            ext_pattern = "$"
        
        escaped_name = re.escape(sequence_name)
        pattern = rf'^{escaped_name}[^a-zA-Z]*?(\d+).*?{ext_pattern}'
        regex = re.compile(pattern)
        
        sequence_files = []
        
        for file in file_list:
            match = regex.match(file)
            if match:
                frame_number = int(match.group(1))
                sequence_files.append(file)
                print(f"Matched: {file} (Frame: {frame_number})")
        
        return sequence_files
