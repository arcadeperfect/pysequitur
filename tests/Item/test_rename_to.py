import pytest
from pathlib import Path
from pysequitur import Item
from pysequitur.file_sequence import Components

def test_rename_to(parse_item_yaml):
    
    
    test_env_list = parse_item_yaml()

    # Test unlinked items (no real file associated)
    for test_case in test_env_list:
        data = test_case['data']    
        item = Item.from_file_name(data['file_name'])
        
        assert isinstance(item, Item)
        assert item.exists is False
        
        # Test prefix rename
        item.rename_to(Components(prefix="new_prefix"))
        assert item.prefix == "new_prefix"
        
        # Test delimiter rename
        item.rename_to(Components(delimiter="_"))
        assert item.delimiter == "_"
        item.rename_to(Components(delimiter="-"))
        assert item.delimiter == "-"
        
        # Test padding rename
        for new_padding in [4, 20, 1]:
            item.rename_to(Components(padding=new_padding))
            min_padding = len(str(data['frame_number']))
            assert item.padding == max(new_padding, min_padding)
        
        # Test suffix and extension rename
        item.rename_to(Components(suffix="new_suffix"))
        assert item.suffix == "new_suffix"
        item.rename_to(Components(extension="new_extension"))
        assert item.extension == "new_extension"

    # Test linked items (with real file associated)
    for test_case in test_env_list:
        data = test_case['data']    
        item = Item.from_file_name(data['file_name'], test_case['real_file'].parent)
        
        assert isinstance(item, Item)
        assert item.exists is True
        
        # Test prefix rename
        original_path = Path(item.absolute_path)
        item.rename_to(Components(prefix="new_prefix"))
        assert item.prefix == "new_prefix"
        assert not original_path.exists()

        # Test delimiter rename
        original_path = Path(item.absolute_path)
        item.rename_to(Components(delimiter="_"))
        assert item.delimiter == "_"
        if not data['delimiter'] == "_":
            assert not original_path.exists()
            
        original_path = Path(item.absolute_path)
        item.rename_to(Components(delimiter="-"))
        assert item.delimiter == "-"
        assert not original_path.exists()

        # Test padding rename
        for new_padding in [data['padding'] + 1, 20, 1]:
            original_path = Path(item.absolute_path)
            item.rename_to(Components(padding=new_padding))
            min_padding = len(str(data['frame_number']))
            assert item.padding == max(new_padding, min_padding)
            assert not original_path.exists()

        # Test suffix and extension rename
        original_path = Path(item.absolute_path)
        item.rename_to(Components(suffix="new_suffix"))
        assert item.suffix == "new_suffix"
        assert not original_path.exists()

        original_path = Path(item.absolute_path)
        item.rename_to(Components(extension="new_extension"))
        assert item.extension == "new_extension"
        assert not original_path.exists()

        assert item.exists is True

# import pytest
# from pathlib import Path
# from pysequitur import Item
# import shutil

# from pysequitur.file_sequence import Components
# # from pysequitur import Item

# def test_item_rename_to(parse_item_yaml):
    
#     filename = "ItemTestData.yaml"
#     test_env = parse_item_yaml(Path(__file__).parent / 'test_data' / filename)

#     # unlinked items (no real file associated)

#     for test_case in test_env:

#         data = test_case['data']    
#         item = Item.from_file_name(data['file_name'])
        
#         assert isinstance(item, Item)
#         assert item.exists is False
        
#         item.rename_to(Components(prefix = "new_prefix"))
#         assert item.prefix == "new_prefix"
        
#         item.rename_to(Components(delimiter="_"))
#         assert item.delimiter == "_"
        
#         item.rename_to(Components(delimiter="-"))
#         assert item.delimiter == "-"
        
#         new_padding = 4
#         item.rename_to(Components(padding=new_padding))
#         min_padding = len(str(data['frame_number']))
#         assert item.padding == max(new_padding, min_padding)
        
#         new_padding = 20
#         item.rename_to(Components(padding=new_padding))
#         min_padding = len(str(data['frame_number']))
#         assert item.padding == max(new_padding, min_padding)
        
#         new_padding = 1
#         item.rename_to(Components(padding=new_padding))
#         min_padding = len(str(data['frame_number']))
#         assert item.padding == max(new_padding, min_padding)
        
#         item.rename_to(Components(suffix="new_suffix"))
#         assert item.suffix == "new_suffix"
        
#         item.rename_to(Components(extension="new_extension"))
#         assert item.extension == "new_extension"
        
        
#     filename = "ItemTestData.yaml"
#     test_env = parse_item_yaml(Path(__file__).parent / 'test_data' / filename)

#     # unlinked items (no real file associated)

#     for test_case in test_env:

#         data = test_case['data']    
#         item = Item.from_file_name(data['file_name'], test_case['real_file'].parent)
        
#         assert isinstance(item, Item)
#         assert item.exists is True
        
#         original_path = Path(item.absolute_path)
#         item.rename_to(Components(prefix = "new_prefix"))
#         assert item.prefix == "new_prefix"
#         assert not original_path.exists()

                
#         original_path = Path(item.absolute_path)
#         item.rename_to(Components(delimiter="_"))
#         assert item.delimiter == "_"
#         if not data['delimiter'] == "_":
#             assert not original_path.exists()

                        
#         original_path = Path(item.absolute_path)
#         item.rename_to(Components(delimiter="-"))
#         assert item.delimiter == "-"
#         assert not original_path.exists()

        
#         original_path = Path(item.absolute_path)
#         new_padding = data['padding'] + 1
#         item.rename_to(Components(padding=new_padding))
#         min_padding = len(str(data['frame_number']))
#         assert item.padding == max(new_padding, min_padding)
#         assert not original_path.exists()

        
#         original_path = Path(item.absolute_path)
#         new_padding = 20
#         item.rename_to(Components(padding=new_padding))
#         min_padding = len(str(data['frame_number']))
#         assert item.padding == max(new_padding, min_padding)
#         assert not original_path.exists()

        
#         original_path = Path(item.absolute_path)
#         new_padding = 1
#         item.rename_to(Components(padding=new_padding))
#         min_padding = len(str(data['frame_number']))
#         assert item.padding == max(new_padding, min_padding)
#         assert not original_path.exists()

        
#         original_path = Path(item.absolute_path)
#         item.rename_to(Components(suffix="new_suffix"))
#         assert item.suffix == "new_suffix"
#         assert not original_path.exists()

        
#         original_path = Path(item.absolute_path)
#         item.rename_to(Components(extension="new_extension"))
#         assert item.extension == "new_extension"
#         assert not original_path.exists()

        
#         assert item.exists is True
