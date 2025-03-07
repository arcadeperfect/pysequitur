import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_file_sequence_offset_frames(tmp_path):
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

    # Test positive offset
    offset_sequence = sequence.offset_frames(10)

    # Assert sequence is modified in place
    assert offset_sequence is sequence

    # Assert files are renamed with new frame numbers
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1011, 1014))
    assert not any(
        (original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004)
    )

    # Assert frame numbers are updated
    assert all(
        item.frame_number == i for item, i in zip(sequence.items, range(1011, 1014))
    )

    # Test negative offset
    offset_sequence = sequence.offset_frames(-15)

    # Assert files are renamed with new frame numbers
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(996, 999))
    assert not any(
        (original_dir / f"test.{i:04d}.exr").exists() for i in range(1011, 1014)
    )

    # Assert frame numbers are updated
    assert all(
        item.frame_number == i for item, i in zip(sequence.items, range(996, 999))
    )

    # Test error on negative frames
    with pytest.raises(ValueError):
        sequence.offset_frames(-1000)  # Would result in negative frame numbers

    # Assert files remain at previous numbers after failed offset
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(996, 999))
