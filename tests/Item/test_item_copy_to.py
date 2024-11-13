import pytest
from pathlib import Path
import shutil
from pysequitur import Item
from pysequitur.file_sequence import Components

def test_item_copy_to(parse_item_yaml):
    print("\n test")
    
    test_env_list = parse_item_yaml()

    # Test unlinked items (no real file associated)
    for test_case in test_env_list:
        data = test_case['data']    
        item = Item.from_file_name(data['file_name'])
        
        assert isinstance(item, Item)
        assert item.exists is False
        
        new_item = item.copy_to()
        assert new_item.prefix == data['prefix'] + '_copy'

    # Test linked items (with real file associated)
    for test_case in test_env_list:
        move_to_dir = Path(test_case['tmp_dir'] / 'move_to')
        move_to_dir.mkdir(parents=True, exist_ok=True)
        
        data = test_case['data']
        item = Item.from_file_name(data['file_name'], test_case['real_file'].parent)
        
        assert isinstance(item, Item)
        original_path = Path(item.absolute_path)
        assert original_path.exists()
        assert item.exists

        # Test copy with new directory
        copied_item_1 = item.copy_to(new_directory=move_to_dir)
        assert copied_item_1.exists
        assert copied_item_1.directory == move_to_dir
        assert copied_item_1.prefix == data['prefix']
        copied_item_1.absolute_path.unlink()
        
        # Test copy with default settings (adds '_copy' to prefix)
        copied_item_2 = item.copy_to()
        assert copied_item_2.exists
        assert copied_item_2.directory == item.directory
        assert copied_item_2.prefix == data['prefix'] + '_copy'
        copied_item_2.absolute_path.unlink()
        
        # Test copy with new prefix
        copied_item_3 = item.copy_to(Components(prefix='new_prefix'))
        assert copied_item_3.exists
        assert copied_item_3.directory == item.directory
        assert copied_item_3.prefix == 'new_prefix'
        copied_item_3.absolute_path.unlink()
        
        shutil.rmtree(move_to_dir)
        
# import pytest
# from pathlib import Path
# from pysequitur import Item
# import shutil

# from pysequitur.file_sequence import Components
# # from pysequitur import Item

# def test_item_copy_to(parse_item_yaml):
    
#     filename = "ItemTestData.yaml"
#     test_env = parse_item_yaml(Path(__file__).parent / 'test_data' / filename)

#     # unlinked items (no real file associated)

#     for test_case in test_env:

#         data = test_case['data']    
#         item = Item.from_file_name(data['file_name'])
        
#         assert isinstance(item, Item)
#         assert item.exists is False
        
#         new_item = item.copy_to()
#         assert new_item.prefix == data['prefix'] + '_copy'

        
#     #linked items (real file associated)
    
#     for test_case in test_env:
        
#         move_to_dir = Path(test_case['tmp_dir'] / 'move_to')
#         move_to_dir.mkdir(parents=True, exist_ok=True)
        
#         data = test_case['data']
#         item = Item.from_file_name(data['file_name'], test_case['real_file'].parent)
        
        
#         assert isinstance(item, Item)
        
#         original_path = Path(item.absolute_path)
#         assert original_path.exists()
#         assert item.exists

#         copied_item_1 = item.copy_to(new_directory= move_to_dir)
        
#         assert copied_item_1.exists
#         assert copied_item_1.directory == move_to_dir
#         assert copied_item_1.prefix == data['prefix']
#         copied_item_1.absolute_path.unlink()
        
#         copied_item_2 = item.copy_to()
        
#         assert copied_item_2.exists
#         assert copied_item_2.directory == item.directory
#         assert copied_item_2.prefix == data['prefix'] + '_copy'
#         copied_item_2.absolute_path.unlink()
        
#         copied_item_3 = item.copy_to(Components(prefix='new_prefix'))
        
#         assert copied_item_3.exists
#         assert copied_item_3.directory == item.directory
#         assert copied_item_3.prefix == 'new_prefix'
#         copied_item_3.absolute_path.unlink()
        
        
#         shutil.rmtree(move_to_dir)
        
        