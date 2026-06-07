import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_file_sequence_offset_frames_without_execute(tmp_path):
    """Test that offset_frames returns proposed state without executing."""
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

    # Test positive offset without execute
    new_sequence, plan = sequence.offset_frames(10)

    # Assert new_sequence is a new instance
    assert new_sequence is not sequence

    # Assert new sequence has correct frame numbers
    assert all(
        item.frame_number == i
        for item, i in zip(new_sequence.items, range(1011, 1014))
    )

    # Assert original sequence is unchanged (frozen)
    assert all(
        item.frame_number == i for item, i in zip(sequence.items, range(1001, 1004))
    )

    # Assert original files still exist and haven't been renamed
    assert all(
        (original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004)
    )
    assert not any(
        (original_dir / f"test.{i:04d}.exr").exists() for i in range(1011, 1014)
    )

    # Test negative offset without execute
    new_sequence, plan = sequence.offset_frames(-10)

    # Assert new sequence has correct frame numbers
    assert all(
        item.frame_number == i
        for item, i in zip(new_sequence.items, range(991, 994))
    )

    # Assert original sequence and files still unchanged
    assert all(
        item.frame_number == i for item, i in zip(sequence.items, range(1001, 1004))
    )
    assert all(
        (original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004)
    )

    # Test that other properties are preserved in new sequence
    for orig_item, new_item in zip(sequence.items, new_sequence.items):
        assert new_item.prefix == orig_item.prefix
        assert new_item.extension == orig_item.extension
        assert new_item.padding == orig_item.padding
        assert new_item.directory == orig_item.directory

    # Test error on negative frames
    with pytest.raises(ValueError):
        sequence.offset_frames(-1002)  # Would result in negative frame numbers
