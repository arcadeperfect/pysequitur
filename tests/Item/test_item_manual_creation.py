from pathlib import Path
from pysequitur import Item
# from pysequitur import Item

def test_item_files(parse_item_yaml):
    
    filename = "ItemTestData.yaml"
    test_env = parse_item_yaml(Path(__file__).parent / 'test_data' / filename)

    for test_case in test_env:

        data = test_case['data']    
        
        item = Item(data['prefix'],
                    data['frame_string'],
                    data['extension'],
                    # test['real_file'],
                    data['delimiter'],
                    data['suffix'],
                    Path(test_case['real_file']).parent)
        

        # # assert item.path.relative_to(test_case['test_dir']) == test_case['real_file'].relative_to(test_case['test_dir'])
        # assert 
        assert item.exists
        assert item.absolute_path == test_case['real_file']
        assert item.prefix == data['prefix']    
        assert item.frame_string == data['frame_string']
        assert item.extension == data['extension']
        assert item.delimiter == data['delimiter']
        assert item.padding == data['padding']
        assert item.suffix == data['suffix']
        assert item.filename == data['file_name']
        assert item.stem == data['file_stem']