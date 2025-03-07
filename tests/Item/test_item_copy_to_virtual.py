import pytest
from pathlib import Path
from pysequitur import Item
from pysequitur.file_sequence import Components


def test_item_copy_to_virtual(tmp_path):
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

    # Test virtual copy with new directory
    virtual_item = item.copy_to(new_directory=new_dir, virtual=True)

    # Assert virtual_item is a new instance (not the same object)
    assert virtual_item is not item

    # Assert virtual_item has correct parameters
    assert virtual_item.directory == new_dir
    assert virtual_item.filename == "test.1001.exr"
    assert virtual_item.path == new_dir / "test.1001.exr"

    # Test virtual copy with default settings (should add '_copy' to prefix)
    virtual_item = item.copy_to(virtual=True)
    assert virtual_item.prefix == "test_copy"
    assert virtual_item.directory == item.directory
    assert virtual_item.filename == "test_copy.1001.exr"

    # Test virtual copy with new Components
    virtual_item = item.copy_to(Components(prefix="new_prefix"), virtual=True)
    assert virtual_item.prefix == "new_prefix"
    assert virtual_item.directory == item.directory
    assert virtual_item.filename == "new_prefix.1001.exr"

    # Test virtual copy with both new directory and Components
    virtual_item = item.copy_to(
        Components(prefix="new_prefix"), new_directory=new_dir, virtual=True
    )
    assert virtual_item.prefix == "new_prefix"
    assert virtual_item.directory == new_dir
    assert virtual_item.filename == "new_prefix.1001.exr"
    assert virtual_item.path == new_dir / "new_prefix.1001.exr"

    # Assert original item and file haven't changed
    assert item.path == original_path
    assert item.prefix == "test"
    assert original_path.exists()

    # Assert no new files were created
    assert not (new_dir / "test.1001.exr").exists()
    assert not (original_dir / "test_copy.1001.exr").exists()
    assert not (original_dir / "new_prefix.1001.exr").exists()
    assert not (new_dir / "new_prefix.1001.exr").exists()
