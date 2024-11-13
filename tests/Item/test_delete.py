import pytest
from pathlib import Path
from pysequitur import Item
# from pysequitur import Item

def test_delete(parse_item_yaml):
    
    filename = "ItemTestData.yaml"
    test_env = parse_item_yaml(Path(__file__).parent / 'test_data' / filename)

    # unlinked items (no real file associated)

    for test_case in test_env:

        data = test_case['data']    
        
        item = Item.from_file_name(data['file_name'])
        
        assert isinstance(item, Item)
        
        assert item.exists is False
        
        with pytest.raises(FileNotFoundError):
            item.delete()
  
        
    # linked items (real file associated)
    
    for test_case in test_env:
        
        data = test_case['data']
        item = Item.from_file_name(data['file_name'], test_case['real_file'].parent)
        
        assert isinstance(item, Item)
        
        assert item.exists
        
        item.delete()

        assert not item.exists