import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_file_sequence_folderize(tmp_path):
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

    # Test folderize
    new_sequence, plan = sequence.folderize("subfolder")
    plan.execute()

    # Assert new_sequence is a new instance (frozen)
    assert new_sequence is not sequence

    # Assert files have been moved to subfolder
    subfolder = original_dir / "subfolder"
    assert subfolder.exists()
    assert all((subfolder / f.name).exists() for f in files)
    assert not any(f.exists() for f in files)  # Original locations empty

    # Assert new sequence has correct directory
    assert all(item.directory == subfolder for item in new_sequence.items)
