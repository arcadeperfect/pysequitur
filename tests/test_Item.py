from pathlib import Path
from pysequitur.file_sequence import Item
import pytest


def test_item(create_Item_test_files):

    test_cases_dir = Path(__file__).parent / 'Item_test_cases'
    yaml_file = test_cases_dir / '1.yaml'

    test_env = create_Item_test_files(yaml_file)

    for test in test_env:
        # print(test['data']['path'])
        # print(test['real_file'].exists())

        data = test['data']

        # print(test['test_dir'])

        item = Item(data['name'],
                    data['frame_number'],
                    data['extension'],
                    test['real_file'],
                    data['separator'],
                    data['post_numeral'])

        assert item.path.relative_to(test['test_dir']) == test['real_file'].relative_to(test['test_dir'])
        assert item.name == data['name']    
        assert item.frame_string == data['frame_number']
        assert item.extension == data['extension']
        assert item.separator == data['separator']
        assert item.padding == data['padding']
        assert item.post_numeral == data['post_numeral']
        assert item.filename == data['file_name']
        assert item.stem == data['file_stem']


    with pytest.raises(ValueError):
        Item('name', '0010', 'exr', Path('pretend'), '.', '_v1')

