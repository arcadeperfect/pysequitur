import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_file_sequence_with_padding_without_execute(tmp_path):
    """Test that with_padding returns proposed state without executing."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create sequence (now uses tuple)
    items = tuple(Item.from_path(f) for f in files)
    sequence = FileSequence(items)

    # Test padding increase without execute
    new_sequence, plan = sequence.with_padding(5)

    # Assert new_sequence is a new instance
    assert new_sequence is not sequence

    # Assert new sequence has correct padding
    assert all(item.padding == 5 for item in new_sequence.items)
    assert all(
        item.frame_string == f"{i:05d}"
        for i, item in zip(range(1001, 1004), new_sequence.items)
    )

    # Assert original sequence hasn't changed (frozen)
    assert all(item.padding == 4 for item in sequence.items)
    assert all(
        item.frame_string == f"{i:04d}"
        for i, item in zip(range(1001, 1004), sequence.items)
    )

    # Assert original files haven't been renamed
    assert all(
        (original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004)
    )
    assert not any(
        (original_dir / f"test.{i:05d}.exr").exists() for i in range(1001, 1004)
    )

    # Test padding decrease without execute (but not below frame number width)
    new_sequence, plan = sequence.with_padding(3)

    # Assert new sequence has correct padding (not below frame number width)
    assert all(
        item.padding == 4 for item in new_sequence.items
    )  # Can't go below 4 for 1001-1003
    assert all(
        item.frame_string == f"{i:04d}"
        for i, item in zip(range(1001, 1004), new_sequence.items)
    )

    # Assert original sequence and files still unchanged
    assert all(item.padding == 4 for item in sequence.items)
    assert all(
        (original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004)
    )

    # Test that other properties are preserved in new sequence
    for orig_item, new_item in zip(sequence.items, new_sequence.items):
        assert new_item.frame_number == orig_item.frame_number
        assert new_item.prefix == orig_item.prefix
        assert new_item.extension == orig_item.extension
        assert new_item.directory == orig_item.directory
