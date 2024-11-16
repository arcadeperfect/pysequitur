from pathlib import Path
from pysequitur import Item

def test_item_from_path(parse_item_yaml):
    
    
    test_env_list = parse_item_yaml()

    for test_case in test_env_list:
        data = test_case['data']    
        item = Item.from_path(test_case['real_file'])
        
        assert isinstance(item, Item)
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

# from pathlib import Path
# from pysequitur import Item
# # from pysequitur import Item

# def test_item_from_path(parse_item_yaml):
    
#     filename = "ItemTestData.yaml"
#     test_env = parse_item_yaml(Path(__file__).parent / 'test_data' / filename)

#     for test_case in test_env:

#         data = test_case['data']    
        
#         item = Item.from_path(test_case['real_file'])
        
#         assert isinstance(item, Item)
        
#         assert item.exists
#         assert item.absolute_path == test_case['real_file']
#         assert item.prefix == data['prefix']    
#         assert item.frame_string == data['frame_string']
#         assert item.extension == data['extension']
#         assert item.delimiter == data['delimiter']
#         assert item.padding == data['padding']
#         assert item.suffix == data['suffix']
#         assert item.filename == data['file_name']
#         assert item.stem == data['file_stem']