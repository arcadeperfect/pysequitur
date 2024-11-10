from pathlib import Path
from pysequitur.file_sequence import FileSequence, Parser
import os

def normalize_empty(value):
    return None if value == '' else value

def compare(actual, expected):
    assert normalize_empty(actual) == normalize_empty(expected)

def test_parse_filename(load_test_cases):
    
    test_cases_dir = Path(__file__).parent / 'Item_test_cases'
    yaml_file = test_cases_dir / '1.yaml'

    cases = load_test_cases(yaml_file)
    
    for case in cases:

        data = case['data']
        item = Parser.item_from_filename(os.path.basename(data['path']))

        compare(item.prefix, data['name'])
        compare(item.frame_string, data['frame_number'])
        compare(item.extension, data['extension'])
        compare(item.delimiter, data['separator'])
        compare(item.suffix, data['post_numeral'])
        compare(item.padding, data['padding'])
