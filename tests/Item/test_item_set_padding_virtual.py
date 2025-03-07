import pytest
from pathlib import Path
from pysequitur import Item


def test_item_set_padding_virtual(tmp_path):
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
    original_padding = item.padding

    # Test virtual padding update
    virtual_item = item.set_padding_to(5, virtual=True)

    # Assert virtual_item is a new instance (not the same object)
    assert virtual_item is not item

    # Assert virtual_item has correct parameters
    assert virtual_item.padding == 5
    assert virtual_item.frame_string == "01001"
    assert virtual_item.filename == "test.01001.exr"

    # Assert original item hasn't changed
    assert item.padding == original_padding
    assert item.frame_string == "1001"
    assert item.path == original_path

    # Test minimum padding (should not go below frame number width)
    virtual_item = item.set_padding_to(2, virtual=True)
    assert virtual_item.padding == 4  # Because "1001" needs 4 digits
    assert virtual_item.frame_string == "1001"

    # Assert original file hasn't been modified
    assert original_path.exists()
    assert not (original_dir / "test.01001.exr").exists()
