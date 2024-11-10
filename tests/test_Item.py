from pathlib import Path
from pysequitur.file_sequence import Item
import pytest


def test_item(create_Item_test_files):

    test_cases_dir = Path(__file__).parent / 'Item_test_cases'
    yaml_file = test_cases_dir / '1.yaml'

    test_env = create_Item_test_files(yaml_file)

    for test_case in test_env:

        data = test_case['data']


        # prefix = data['name']
        # frame_string = data['frame_number']
        # delimiter = data['separator']
        # extension = data['extension']
        # suffix = data['post_numeral']
        # t = test_case['real_file']
        # directory = str(Path(t).parent)  

        item = Item(data['name'],
                    data['frame_number'],
                    data['extension'],
                    # test['real_file'],
                    data['separator'],
                    data['post_numeral'],
                    Path(test_case['real_file']).parent)

        assert item.path.relative_to(test_case['test_dir']) == test_case['real_file'].relative_to(test_case['test_dir'])
        assert item.prefix == data['name']    
        assert item.frame_string == data['frame_number']
        assert item.extension == data['extension']
        assert item.delimiter == data['separator']
        assert item.padding == data['padding']
        assert item.suffix == data['post_numeral']
        assert item.filename == data['file_name']
        assert item.stem == data['file_stem']


    # with pytest.raises(ValueError):
    #     Item('name', '0010', 'exr', Path('pretend'), '.', '_v1')