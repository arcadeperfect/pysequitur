from pysequitur import Item

def test_item_set_padding():
    
    file = "render_0001.exr"
    
    item = Item.from_file_name(file)
    
    assert isinstance(item, Item)
    assert item.padding == 4
    assert item.frame_string == "0001"
    
    item.padding = 5
    assert item.padding == 5
    assert item.frame_string == "00001"
    
    item.padding = 3
    assert item.padding == 3
    assert item.frame_string == "001"
    
    item.padding = 1
    assert item.padding == 1
    assert item.frame_string == "1"
    
    
    

    file = "render2.0999.exr"
    
    item = Item.from_file_name(file)
    
    assert isinstance(item, Item)
    assert item.padding == 4
    assert item.frame_string == "0999"
    
    item.padding = 5
    assert item.padding == 5
    assert item.frame_string == "00999"
    
    item.padding = 3
    assert item.padding == 3
    assert item.frame_string == "999"
    
    item.padding = 2
    assert item.padding == 3
    assert item.frame_string == "999"
    
    item.padding = 1
    assert item.padding == 3
    assert item.frame_string == "999"
    
    
    
    file = "render3_0999_suffix.exr"
    
    item = Item.from_file_name(file)
    
    assert isinstance(item, Item)
    assert item.padding == 4
    assert item.frame_string == "0999"
    
    item.padding = 5
    assert item.padding == 5
    assert item.frame_string == "00999"
    
    item.padding = 3
    assert item.padding == 3
    assert item.frame_string == "999"
    
    item.padding = 2
    assert item.padding == 3
    assert item.frame_string == "999"
    
    item.padding = 1
    assert item.padding == 3
    assert item.frame_string == "999"
     