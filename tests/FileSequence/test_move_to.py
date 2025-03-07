import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_file_sequence_move_to(tmp_path):
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

    # Test move to non-existent directory without create_directory flag
    new_dir = tmp_path / "new"
    with pytest.raises(FileNotFoundError):
        sequence.move_to(new_dir)

    # Assert files are still in original location after failed move
    assert all(f.exists() for f in files)

    # Test move with create_directory flag
    moved_sequence = sequence.move_to(new_dir, create_directory=True)

    # Assert moved_sequence is the same instance (modified in place)
    assert moved_sequence is sequence

    # Assert files exist in new location
    assert all((new_dir / f.name).exists() for f in files)
    # Assert files no longer exist in original location
    assert not any(f.exists() for f in files)

    # Test move to nested non-existent directory
    nested_dir = tmp_path / "nested" / "path"
    with pytest.raises(FileNotFoundError):
        sequence.move_to(nested_dir)

    # Assert files are still in previous location after failed move
    assert all((new_dir / f.name).exists() for f in files)

    # Test move to nested directory with create_directory flag
    moved_sequence = sequence.move_to(nested_dir, create_directory=True)

    # Assert files exist in new nested location
    assert all((nested_dir / f.name).exists() for f in files)
    # Assert files no longer exist in previous location
    assert not any((new_dir / f.name).exists() for f in files)

    # Assert sequence has correct parameters
    assert all(item.directory == nested_dir for item in sequence.items)
    assert all(
        item.filename == f"test.{i:04d}.exr"
        for i, item in zip(range(1001, 1004), sequence.items)
    )

    # Test that frame numbers and other properties are preserved
    for i, item in enumerate(sequence.items):
        assert item.frame_number == 1001 + i
        assert item.prefix == "test"
        assert item.extension == "exr"
        assert item.padding == 4
