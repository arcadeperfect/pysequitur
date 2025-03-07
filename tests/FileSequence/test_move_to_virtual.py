import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_file_sequence_move_to_virtual(tmp_path):
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
    if None in items:
        raise ValueError("None in items")
    sequence = FileSequence(items) # type: ignore

    new_dir = tmp_path / "new"

    # Test virtual move
    virtual_sequence = sequence.move_to(new_dir, virtual=True)

    # Assert virtual_sequence is a new instance
    assert virtual_sequence is not sequence

    # Assert virtual_sequence has correct parameters
    assert all(item.directory == new_dir for item in virtual_sequence.items)
    assert len(virtual_sequence.items) == len(sequence.items)

    # Assert original sequence hasn't changed
    assert all(item.directory == original_dir for item in sequence.items)

    # Assert original files still exist and new files don't
    assert all(f.exists() for f in files)
    assert not new_dir.exists() or not any((new_dir / f.name).exists() for f in files)

    # Test that frame numbers and other properties are preserved
    for orig_item, virtual_item in zip(sequence.items, virtual_sequence.items):
        assert virtual_item.frame_number == orig_item.frame_number
        assert virtual_item.prefix == orig_item.prefix
        assert virtual_item.extension == orig_item.extension
        assert virtual_item.padding == orig_item.padding
        assert virtual_item.filename == orig_item.filename
