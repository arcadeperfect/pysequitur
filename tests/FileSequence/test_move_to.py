import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_file_sequence_move(tmp_path):
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

    # Test move to non-existent directory without create_directory flag
    new_dir = tmp_path / "new"
    moved_sequence, plan = sequence.move(new_dir)
    result = plan.execute()
    # Should fail because directory doesn't exist
    assert not result.success
    assert len(result.failed) > 0

    # Assert files are still in original location after failed move
    assert all(f.exists() for f in files)

    # Test move with create_directory flag
    moved_sequence, plan = sequence.move(new_dir, create_directory=True)
    plan.execute()

    # Assert moved_sequence is a new instance (frozen)
    assert moved_sequence is not sequence

    # Assert files exist in new location
    assert all((new_dir / f.name).exists() for f in files)
    # Assert files no longer exist in original location
    assert not any(f.exists() for f in files)

    # Continue with the moved sequence
    sequence = moved_sequence

    # Test move to nested non-existent directory
    nested_dir = tmp_path / "nested" / "path"
    moved_sequence, plan = sequence.move(nested_dir)
    result = plan.execute()
    # Should fail because directory doesn't exist
    assert not result.success
    assert len(result.failed) > 0

    # Assert some files may still be in previous location after failed move
    # (partial failure - some operations may have succeeded before the failure)

    # Test move to nested directory with create_directory flag
    moved_sequence, plan = sequence.move(nested_dir, create_directory=True)
    plan.execute()

    # Assert files exist in new nested location
    assert all((nested_dir / f.name).exists() for f in files)
    # Assert files no longer exist in previous location
    assert not any((new_dir / f.name).exists() for f in files)

    # Assert new sequence has correct parameters
    assert all(item.directory == nested_dir for item in moved_sequence.items)
    assert all(
        item.filename == f"test.{i:04d}.exr"
        for i, item in zip(range(1001, 1004), moved_sequence.items)
    )

    # Test that frame numbers and other properties are preserved
    for i, item in enumerate(moved_sequence.items):
        assert item.frame_number == 1001 + i
        assert item.prefix == "test"
        assert item.extension == "exr"
        assert item.padding == 4
