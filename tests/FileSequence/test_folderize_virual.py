import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_file_sequence_set_padding_virtual(tmp_path):
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

    # Test virtual padding increase
    virtual_sequence = sequence.set_padding_to(5, virtual=True)

    # Assert virtual_sequence is a new instance
    assert virtual_sequence is not sequence

    # Assert virtual sequence has correct padding
    assert all(item.padding == 5 for item in virtual_sequence.items)
    assert all(
        item.frame_string == f"{i:05d}"
        for i, item in zip(range(1001, 1004), virtual_sequence.items)
    )

    # Assert original sequence hasn't changed
    assert all(item.padding == 4 for item in sequence.items)
    assert all(
        item.frame_string == f"{i:04d}"
        for i, item in zip(range(1001, 1004), sequence.items)
    )

    # Assert original files haven't been renamed
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))
    assert not any(
        (original_dir / f"test.{i:05d}.exr").exists() for i in range(1001, 1004)
    )

    # Test virtual padding decrease (but not below frame number width)
    virtual_sequence = sequence.set_padding_to(3, virtual=True)

    # Assert virtual sequence has correct padding (not below frame number width)
    assert all(
        item.padding == 4 for item in virtual_sequence.items
    )  # Can't go below 4 for 1001-1003
    assert all(
        item.frame_string == f"{i:04d}"
        for i, item in zip(range(1001, 1004), virtual_sequence.items)
    )

    # Assert original sequence and files still unchanged
    assert all(item.padding == 4 for item in sequence.items)
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))

    # Test that other properties are preserved in virtual sequence
    for orig_item, virtual_item in zip(sequence.items, virtual_sequence.items):
        assert virtual_item.frame_number == orig_item.frame_number
        assert virtual_item.prefix == orig_item.prefix
        assert virtual_item.extension == orig_item.extension
        assert virtual_item.directory == orig_item.directory
