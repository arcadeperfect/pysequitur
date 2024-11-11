from pathlib import Path
from pysequitur.file_sequence import Item, Parser, Components
import pytest
import os


def test_item_setFrameNumber(create_files_from_list):


    #### ----  test linked item


    files = ["frame.0001.jpg"]

    paths = create_files_from_list(files)

    item = Item.from_path(paths[0])

    assert item.exists is True
    assert item.frame_number == 1
    assert item.frame_string == "0001"

    item.set_frame_number(2)

    assert item.exists is True
    assert item.frame_number == 2
    assert item.frame_string == "0002"

    with pytest.raises(ValueError):
        item.set_frame_number(-1)

    item.set_frame_number(1, 1)

    assert item.exists is True
    assert item.frame_number == 1
    assert item.frame_string == "1"

    item.set_frame_number(1, 5)

    assert item.exists is True
    assert item.frame_number == 1
    assert item.frame_string == "00001"

    item.set_frame_number(100, 1)

    assert item.exists is True
    assert item.frame_number == 100
    assert item.frame_string == "100"

    files = ["frame.0001.jpg"]
    paths = create_files_from_list(files)
    item = Item.from_path(paths[0])

    # Test consecutive changes
    item.set_frame_number(2)
    item.set_frame_number(3)
    assert item.frame_number == 3
    assert item.frame_string == "0003"

    # Test setting same number (should not change padding)
    item.set_frame_number(3, 4)  # Set padding to 4
    assert item.frame_string == "0003"
    item.set_frame_number(3)  # Should maintain padding
    assert item.frame_string == "0003"

    # Test large numbers affecting padding
    item.set_frame_number(10000, 3)  # Padding should adjust to fit number
    assert item.frame_string == "10000"  # 5 digits because number needs it

    # Test padding smaller than number length
    item.set_frame_number(100, 2)  # Should use 3 digits because 100 needs it
    assert item.frame_string == "100"

    # Test maximum padding
    item.set_frame_number(1, 10)
    assert item.frame_string == "0000000001"

    # Test zero
    item.set_frame_number(0)
    assert item.frame_number == 0
    assert item.frame_string == "0000000000"  # Should maintain previous padding

    # Test frame number at padding boundary
    item.set_frame_number(999, 3)
    assert item.frame_string == "999"
    item.set_frame_number(1000, 3)  # Should auto-adjust to 4 digits
    assert item.frame_string == "1000"





    #### ----  test unlinked item

    item = Item(
        prefix="frame",
        delimiter=".",
        frame_string="0001",
        extension="jpg",
        directory= None
    )

    item.set_frame_number(2)


    assert item.frame_number == 2
    assert item.frame_string == "0002"

    with pytest.raises(ValueError):
        item.set_frame_number(-1)

    item.set_frame_number(1, 1)


    assert item.frame_number == 1
    assert item.frame_string == "1"

    item.set_frame_number(1, 5)


    assert item.frame_number == 1
    assert item.frame_string == "00001"

    item.set_frame_number(100, 1)


    assert item.frame_number == 100
    assert item.frame_string == "100"

    files = ["frame.0001.jpg"]
    paths = create_files_from_list(files)
    item = Item.from_path(paths[0])

    # Test consecutive changes
    item.set_frame_number(2)
    item.set_frame_number(3)
    assert item.frame_number == 3
    assert item.frame_string == "0003"

    # Test setting same number (should not change padding)
    item.set_frame_number(3, 4)  # Set padding to 4
    assert item.frame_string == "0003"
    item.set_frame_number(3)  # Should maintain padding
    assert item.frame_string == "0003"

    # Test large numbers affecting padding
    item.set_frame_number(10000, 3)  # Padding should adjust to fit number
    assert item.frame_string == "10000"  # 5 digits because number needs it

    # Test padding smaller than number length
    item.set_frame_number(100, 2)  # Should use 3 digits because 100 needs it
    assert item.frame_string == "100"

    # Test maximum padding
    item.set_frame_number(1, 10)
    assert item.frame_string == "0000000001"

    # Test zero
    item.set_frame_number(0)
    assert item.frame_number == 0
    assert item.frame_string == "0000000000"  # Should maintain previous padding

    # Test frame number at padding boundary
    item.set_frame_number(999, 3)
    assert item.frame_string == "999"
    item.set_frame_number(1000, 3)  # Should auto-adjust to 4 digits
    assert item.frame_string == "1000"