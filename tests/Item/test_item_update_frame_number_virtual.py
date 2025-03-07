import pytest
from pathlib import Path
from pysequitur import Item


def test_item_update_frame_number_virtual(tmp_path):
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    test_file = original_dir / "test.1001.exr"
    test_file.touch()

    # Create original item
    item = Item.from_path(test_file)
    if item is None:
        raise ValueError("Item is None")
    original_path = item.path
    original_frame = item.frame_number
    original_padding = item.padding

    # Test virtual frame number update
    virtual_item = item.update_frame_number(2000, virtual=True)

    # Assert virtual_item is a new instance (not the same object)
    assert virtual_item is not item

    # Assert virtual_item has correct parameters
    assert virtual_item.frame_number == 2000
    assert virtual_item.frame_string == "2000"
    assert virtual_item.filename == "test.2000.exr"

    # Assert original item hasn't changed
    assert item.frame_number == original_frame
    assert item.padding == original_padding
    assert item.path == original_path

    # Test virtual frame number update with padding
    virtual_item = item.update_frame_number(2000, padding=5, virtual=True)

    # Assert padding is respected
    assert virtual_item.frame_string == "02000"
    assert virtual_item.filename == "test.02000.exr"

    # Assert original file hasn't been modified
    assert original_path.exists()
    assert not (original_dir / "test.2000.exr").exists()
    assert not (original_dir / "test.02000.exr").exists()
