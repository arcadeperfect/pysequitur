import pytest
from pathlib import Path
from pysequitur import Item, FileSequence
from pysequitur.file_sequence import Components


def test_file_sequence_copy_to_virtual(tmp_path):
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create sequence
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence(items)

    new_dir = tmp_path / "new"

    # Test virtual copy with new directory
    virtual_sequence = sequence.copy_to(new_directory=new_dir, virtual=True)

    # Assert virtual_sequence is a new instance
    assert virtual_sequence is not sequence

    # Assert virtual_sequence has correct parameters
    assert all(item.directory == new_dir for item in virtual_sequence.items)
    assert len(virtual_sequence.items) == len(sequence.items)
    assert all(item.prefix == "test" for item in virtual_sequence.items)

    # Test virtual copy with default settings (should add '_copy' to prefix)
    virtual_sequence = sequence.copy_to(virtual=True)
    assert all(item.prefix == "test_copy" for item in virtual_sequence.items)
    assert all(item.directory == original_dir for item in virtual_sequence.items)

    # Test virtual copy with new Components
    virtual_sequence = sequence.copy_to(Components(prefix="new_prefix"), virtual=True)
    assert all(item.prefix == "new_prefix" for item in virtual_sequence.items)
    assert all(item.directory == original_dir for item in virtual_sequence.items)

    # Test virtual copy with both new directory and Components
    virtual_sequence = sequence.copy_to(
        Components(prefix="new_prefix"), new_directory=new_dir, virtual=True
    )
    assert all(item.prefix == "new_prefix" for item in virtual_sequence.items)
    assert all(item.directory == new_dir for item in virtual_sequence.items)

    # Assert original sequence hasn't changed
    assert all(item.directory == original_dir for item in sequence.items)
    assert all(item.prefix == "test" for item in sequence.items)

    # Assert original files still exist and no new files created
    assert all(f.exists() for f in files)
    assert not new_dir.exists() or not any((new_dir / f.name).exists() for f in files)
    assert not any(
        (original_dir / f"test_copy.{i:04d}.exr").exists() for i in range(1001, 1004)
    )
    assert not any(
        (original_dir / f"new_prefix.{i:04d}.exr").exists() for i in range(1001, 1004)
    )

    # Test that frame numbers and other properties are preserved
    for orig_item, virtual_item in zip(sequence.items, virtual_sequence.items):
        assert virtual_item.frame_number == orig_item.frame_number
        assert virtual_item.extension == orig_item.extension
        assert virtual_item.padding == orig_item.padding
