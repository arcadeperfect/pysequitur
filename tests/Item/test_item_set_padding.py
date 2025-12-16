from pysequitur import Item


def test_item_with_padding():
    file = "render_0001.exr"

    item = Item.from_file_name(file)

    assert isinstance(item, Item)
    assert item.padding == 4
    assert item.frame_string == "0001"

    new_item, plan = item.with_padding(5)
    assert new_item.padding == 5
    assert new_item.frame_string == "00001"

    new_item, plan = item.with_padding(3)
    assert new_item.padding == 3
    assert new_item.frame_string == "001"

    new_item, plan = item.with_padding(1)
    assert new_item.padding == 1
    assert new_item.frame_string == "1"

    file = "render2.0999.exr"

    item = Item.from_file_name(file)

    assert isinstance(item, Item)
    assert item.padding == 4
    assert item.frame_string == "0999"

    new_item, plan = item.with_padding(5)
    assert new_item.padding == 5
    assert new_item.frame_string == "00999"

    new_item, plan = item.with_padding(3)
    assert new_item.padding == 3
    assert new_item.frame_string == "999"

    # Minimum padding is determined by frame number width
    new_item, plan = item.with_padding(2)
    assert new_item.padding == 3  # "999" needs 3 digits minimum
    assert new_item.frame_string == "999"

    new_item, plan = item.with_padding(1)
    assert new_item.padding == 3
    assert new_item.frame_string == "999"

    file = "render3_0999_suffix.exr"

    item = Item.from_file_name(file)

    assert isinstance(item, Item)
    assert item.padding == 4
    assert item.frame_string == "0999"

    new_item, plan = item.with_padding(5)
    assert new_item.padding == 5
    assert new_item.frame_string == "00999"

    new_item, plan = item.with_padding(3)
    assert new_item.padding == 3
    assert new_item.frame_string == "999"

    new_item, plan = item.with_padding(2)
    assert new_item.padding == 3
    assert new_item.frame_string == "999"

    new_item, plan = item.with_padding(1)
    assert new_item.padding == 3
    assert new_item.frame_string == "999"
