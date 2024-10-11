import yaml
from pathlib import Path
import pytest

from pysequitur.file_sequence import Item

def load_test_cases():
    test_cases_dir = Path(__file__).parent / 'Item_test_cases'
    for yaml_file in test_cases_dir.glob('*.yaml'):
        with open(yaml_file, 'r') as f:
            test_cases = yaml.safe_load(f)
            for test_case in test_cases:
                yield test_case

@pytest.mark.parametrize("test_case", load_test_cases())
def test_Item(test_case):
    # Create an Item instance with the input path

    description = test_case['description']
    print(description)

    absolute = Path((test_case['data']['file_absolute_path']))
    directory = Path((test_case['data']['directory']))
    name = test_case['data']['name']
    frame_number = test_case['data']['frame_number']
    extension = test_case['data']['extension']
    separator = test_case['data']['separator']
    padding = test_case['data']['padding']
    stem = test_case['data']['file_stem']
    file_name = test_case['data']['file_name']
    post_numeral = test_case['data']['post_numeral']

    item = Item(name, frame_number, extension, directory, separator, post_numeral)

    assert item.path == absolute
    assert item.name == name
    assert item.frame == frame_number
    assert item.extension == extension
    assert item.separator == separator
    assert item.padding == padding
    assert item.path.stem == stem
    assert item.filename == file_name
    assert item.post_numeral == post_numeral