import pytest
from pathlib import Path
from pysequitur import Item


def test_item_with_padding_without_execute(tmp_path):
    """Test that with_padding returns proposed state without executing."""
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

    # Test padding update without execute
    new_item, plan = item.with_padding(5)

    # Assert new_item is a new instance (not the same object)
    assert new_item is not item

    # Assert new_item has correct parameters
    assert new_item.padding == 5
    assert new_item.frame_string == "01001"
    assert new_item.filename == "test.01001.exr"

    # Assert original item hasn't changed (frozen)
    assert item.padding == original_padding
    assert item.frame_string == "1001"
    assert item.path == original_path

    # Test minimum padding (should not go below frame number width)
    new_item, plan = item.with_padding(2)
    assert new_item.padding == 4  # Because "1001" needs 4 digits
    assert new_item.frame_string == "1001"

    # Assert original file hasn't been modified
    assert original_path.exists()
    assert not (original_dir / "test.01001.exr").exists()
