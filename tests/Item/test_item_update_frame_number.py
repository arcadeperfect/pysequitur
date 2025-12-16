from pathlib import Path
from pysequitur import Item


def test_with_frame_number(parse_item_yaml, tmp_path):
    file = "render.0001.exr"
    item = Item.from_file_name(file)

    assert isinstance(item, Item)
    assert item.frame_number == 1
    assert item.frame_string == "0001"

    new_item, plan = item.with_frame_number(2)
    assert new_item.frame_number == 2
    assert new_item.frame_string == "0002"

    new_item, plan = item.with_frame_number(2, 5)
    assert new_item.frame_number == 2
    assert new_item.frame_string == "00002"

    new_item, plan = item.with_frame_number(2, 1)
    assert new_item.frame_number == 2
    assert new_item.frame_string == "2"

    new_item, plan = item.with_frame_number(1000, 1)
    assert new_item.frame_number == 1000
    assert new_item.frame_string == "1000"
    assert new_item.padding == 4

    file = "render_0001.exr"
    item = Item.from_file_name(file)

    assert isinstance(item, Item)
    assert item.frame_number == 1
    assert item.frame_string == "0001"

    new_item, plan = item.with_frame_number(2)
    assert new_item.frame_number == 2
    assert new_item.frame_string == "0002"

    new_item, plan = item.with_frame_number(2, 5)
    assert new_item.frame_number == 2
    assert new_item.frame_string == "00002"

    new_item, plan = item.with_frame_number(2, 1)
    assert new_item.frame_number == 2
    assert new_item.frame_string == "2"

    new_item, plan = item.with_frame_number(1000, 1)
    assert new_item.frame_number == 1000
    assert new_item.frame_string == "1000"
    assert new_item.padding == 4

    file = "render0001_suffix.exr"
    item = Item.from_file_name(file)

    assert isinstance(item, Item)
    assert item.frame_number == 1
    assert item.frame_string == "0001"

    new_item, plan = item.with_frame_number(2)
    assert new_item.frame_number == 2
    assert new_item.frame_string == "0002"

    new_item, plan = item.with_frame_number(2, 5)
    assert new_item.frame_number == 2
    assert new_item.frame_string == "00002"

    new_item, plan = item.with_frame_number(2, 1)
    assert new_item.frame_number == 2
    assert new_item.frame_string == "2"

    new_item, plan = item.with_frame_number(1000, 1)
    assert new_item.frame_number == 1000
    assert new_item.frame_string == "1000"
    assert new_item.padding == 4
