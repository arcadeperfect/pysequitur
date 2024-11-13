import pytest
from pathlib import Path
from pysequitur import Item
from pysequitur.file_sequence import Components

def test_item_check_rename(parse_item_yaml):
    print("\n test")
    
    test_env_list = parse_item_yaml()

    # Test unlinked items (no real file associated)
    for test_case in test_env_list:
        data = test_case['data']    
        item = Item.from_file_name(data['file_name'])
        
        assert isinstance(item, Item)
        assert item.exists is False

        check_rename = item.check_rename(Components(prefix="new_prefix"))
        assert check_rename[2] is False

    # Test linked items (with real file associated)
    for test_case in test_env_list:
        data = test_case['data']    
        item = Item.from_file_name(data['file_name'], test_case['real_file'].parent)
        
        assert isinstance(item, Item)
        assert item.exists is True
        
        check_rename = item.check_rename(Components(prefix="new_prefix"))
        assert check_rename[0] == item.absolute_path
        assert check_rename[2] is False
        
        new_path = check_rename[1]
        new_path.touch()
        assert new_path.exists()
        assert item.check_rename(Components(prefix="new_prefix"))[2] is True
        new_path.unlink()

# import pytest
# from pathlib import Path
# from pysequitur import Item
# import shutil

# from pysequitur.file_sequence import Components
# # from pysequitur import Item

# def test_item_check_rename(parse_item_yaml):
    
#     filename = "ItemTestData.yaml"
#     test_env = parse_item_yaml(Path(__file__).parent / 'test_data' / filename)

#     # unlinked items (no real file associated)

#     for test_case in test_env:

#         data = test_case['data']    
#         item = Item.from_file_name(data['file_name'])
        
#         assert isinstance(item, Item)
#         assert item.exists is False

#         check_rename = item.check_rename(Components(prefix = "new_prefix"))
#         assert check_rename[2] is False
        
        
#     filename = "ItemTestData.yaml"
#     test_env = parse_item_yaml(Path(__file__).parent / 'test_data' / filename)

#     # unlinked items (no real file associated)

#     for test_case in test_env:

#         data = test_case['data']    
#         item = Item.from_file_name(data['file_name'], test_case['real_file'].parent)
        
#         assert isinstance(item, Item)
#         assert item.exists is True
        
#         check_rename = item.check_rename(Components(prefix = "new_prefix"))
#         assert check_rename[0] == item.absolute_path
#         assert check_rename[2] is False
        
#         new_path = check_rename[1]
#         new_path.touch()
#         assert new_path.exists()
#         assert item.check_rename(Components(prefix = "new_prefix"))[2] is True
#         new_path.unlink()