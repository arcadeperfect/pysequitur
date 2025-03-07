import pytest
from pathlib import Path
from pysequitur import Item


def test_item_move_to_virtual(tmp_path):
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    test_file = original_dir / "test.1001.exr"
    test_file.touch()

    new_dir = tmp_path / "new"

    # Create original item
    item = Item.from_path(test_file)
    if item is None:
        raise ValueError("Item is None")
    original_path = item.path

    # Test virtual move
    virtual_item = item.move_to(new_dir, virtual=True)

    # Assert virtual_item is a new instance (not the same object)
    assert virtual_item is not item

    # Assert virtual_item has correct parameters
    assert virtual_item.directory == new_dir
    assert virtual_item.filename == "test.1001.exr"
    assert virtual_item.path == new_dir / "test.1001.exr"

    # Assert original file hasn't moved
    assert original_path.exists()
    assert item.path == original_path
    assert not (new_dir / "test.1001.exr").exists()
