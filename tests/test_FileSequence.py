from pysequitur.file_sequence import FileSequence, Parser
from pathlib import Path

def normalize_empty(value):
    return None if value == '' else value

def compare(actual, expected):
    assert normalize_empty(actual) == normalize_empty(expected)

def test_filesequence(load_test_cases):

    test_cases_dir = Path(__file__).parent / 'FileSequence_test_cases'
    yaml_file = test_cases_dir / '1.yaml'

    cases = load_test_cases(yaml_file)

    for case in cases:
        data = case['data']

        sequence = Parser.from_file_list(data['files'])[0]

        compare(sequence.prefix, data['name'])
        compare(sequence.first_frame, data['first_frame'])
        compare(sequence.last_frame, data['last_frame'])
        compare(sequence.extension, data['extension'])
        compare(sequence.delimiter, data['separator'])
        compare(sequence.suffix, data['post_numeral'])
        compare(sequence.existing_frames, data['existing_frames'])
        compare(list(sequence.missing_frames), data['missing_frames'])
        compare(sequence.frame_count, data['frames_count'])
        compare(sequence.padding, data['padding'])