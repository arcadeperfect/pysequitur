import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_file_sequence_folderize_without_execute(tmp_path):
    """Test that folderize returns proposed state without executing."""
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

    # Test folderize without execute
    new_sequence, plan = sequence.folderize("subfolder")

    # Assert new_sequence is a new instance
    assert new_sequence is not sequence

    # Assert new sequence has correct directory
    subfolder = original_dir / "subfolder"
    assert all(item.directory == subfolder for item in new_sequence.items)

    # Assert original files still exist and haven't been moved
    assert all(f.exists() for f in files)

    # Assert subfolder doesn't exist yet (since we didn't execute)
    # Note: create_directory=True in folderize may create the directory
    # but files shouldn't be moved
    for f in files:
        assert f.exists()  # Original files still there
        assert not (subfolder / f.name).exists()  # Not moved to subfolder
