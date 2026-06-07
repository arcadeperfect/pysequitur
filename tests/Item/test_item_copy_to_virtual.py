import pytest
from pathlib import Path
from pysequitur import Item
from pysequitur.file_sequence import Components


def test_item_copy_without_execute(tmp_path):
    """Test that copy returns proposed state without executing."""
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

    # Test copy without execute - with new directory
    new_item, plan = item.copy(new_directory=new_dir)

    # Assert new_item is a new instance (not the same object)
    assert new_item is not item

    # Assert new_item has correct parameters
    assert new_item.directory == new_dir
    assert new_item.filename == "test.1001.exr"
    assert new_item.path == new_dir / "test.1001.exr"

    # Test copy without execute - default settings (should add '_copy' to prefix)
    new_item, plan = item.copy()
    assert new_item.prefix == "test_copy"
    assert new_item.directory == item.directory
    assert new_item.filename == "test_copy.1001.exr"

    # Test copy without execute - with new Components
    new_item, plan = item.copy(Components(prefix="new_prefix"))
    assert new_item.prefix == "new_prefix"
    assert new_item.directory == item.directory
    assert new_item.filename == "new_prefix.1001.exr"

    # Test copy without execute - both new directory and Components
    new_item, plan = item.copy(
        Components(prefix="new_prefix"), new_directory=new_dir
    )
    assert new_item.prefix == "new_prefix"
    assert new_item.directory == new_dir
    assert new_item.filename == "new_prefix.1001.exr"
    assert new_item.path == new_dir / "new_prefix.1001.exr"

    # Assert original item and file haven't changed
    assert item.path == original_path
    assert item.prefix == "test"
    assert original_path.exists()

    # Assert no new files were created (we didn't execute)
    assert not (new_dir / "test.1001.exr").exists()
    assert not (original_dir / "test_copy.1001.exr").exists()
    assert not (original_dir / "new_prefix.1001.exr").exists()
    assert not (new_dir / "new_prefix.1001.exr").exists()
