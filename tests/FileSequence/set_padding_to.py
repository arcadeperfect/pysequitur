import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_file_sequence_set_padding(tmp_path):
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

    # Test increasing padding
    padded_sequence = sequence.set_padding_to(5)

    # Assert sequence is modified in place
    assert padded_sequence is sequence

    # Assert files are renamed with new padding
    assert all((original_dir / f"test.{i:05d}.exr").exists() for i in range(1001, 1004))
    assert not any(
        (original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004)
    )

    # Assert padding is updated
    assert all(item.padding == 5 for item in sequence.items)
    assert all(
        item.frame_string == f"{i:05d}"
        for i, item in zip(range(1001, 1004), sequence.items)
    )

    # Test decreasing padding (but not below frame number width)
    padded_sequence = sequence.set_padding_to(3)

    # Assert files are renamed with new padding
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))
    assert not any(
        (original_dir / f"test.{i:05d}.exr").exists() for i in range(1001, 1004)
    )

    # Assert padding is updated (but not below frame number width)
    assert all(
        item.padding == 4 for item in sequence.items
    )  # Can't go below 4 for 1001-1003
    assert all(
        item.frame_string == f"{i:04d}"
        for i, item in zip(range(1001, 1004), sequence.items)
    )
