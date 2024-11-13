from pathlib import Path
from pysequitur import Item

def test_item_frame_number(parse_item_yaml):
    print("\n test")
    
    test_env_list = parse_item_yaml()

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
        assert item.frame_number == data['frame_number']

# from pathlib import Path
# from pysequitur import Item
# # from pysequitur import Item

# def test_item_frame_number(parse_item_yaml):
    
#     filename = "ItemTestData.yaml"
#     test_env = parse_item_yaml(Path(__file__).parent / 'test_data' / filename)

#     for test_case in test_env:

#         data = test_case['data']    
        
#         item = Item(data['prefix'],
#                     data['frame_string'],
#                     data['extension'],
#                     # test['real_file'],
#                     data['delimiter'],
#                     data['suffix'],
#                     Path(test_case['real_file']).parent)
        

#         # # assert item.path.relative_to(test_case['test_dir']) == test_case['real_file'].relative_to(test_case['test_dir'])
#         # assert 
#         assert item.exists
#         assert item.frame_number == data['frame_number']