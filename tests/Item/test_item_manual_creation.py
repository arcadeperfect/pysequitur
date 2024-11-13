from pathlib import Path
from pysequitur import Item

def test_item_files(parse_item_yaml):
    
    print("\n test")
    
    test_env_list = parse_item_yaml()  # No need to pass any arguments

    for test_case in test_env_list:
        data = test_case['data']
        
        item = Item(
            data['prefix'],
            data['frame_string'],
            data['extension'],
            data['delimiter'],
            data['suffix'],
            Path(test_case['real_file']).parent
        )

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
