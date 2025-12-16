import pytest
from pathlib import Path
from pysequitur import Item, FileSequence
from pysequitur.file_sequence import Components


def test_file_sequence_copy_without_execute(tmp_path):
    """Test that copy returns proposed state without executing."""
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

    new_dir = tmp_path / "new"

    # Test copy without execute - with new directory
    new_sequence, plan = sequence.copy(new_directory=new_dir)

    # Assert new_sequence is a new instance
    assert new_sequence is not sequence

    # Assert new_sequence has correct parameters
    assert all(item.directory == new_dir for item in new_sequence.items)
    assert len(new_sequence.items) == len(sequence.items)
    assert all(item.prefix == "test" for item in new_sequence.items)

    # Test copy without execute - default settings (should add '_copy' to prefix)
    new_sequence, plan = sequence.copy()
    assert all(item.prefix == "test_copy" for item in new_sequence.items)
    assert all(item.directory == original_dir for item in new_sequence.items)

    # Test copy without execute - with new Components
    new_sequence, plan = sequence.copy(Components(prefix="new_prefix"))
    assert all(item.prefix == "new_prefix" for item in new_sequence.items)
    assert all(item.directory == original_dir for item in new_sequence.items)

    # Test copy without execute - both new directory and Components
    new_sequence, plan = sequence.copy(
        Components(prefix="new_prefix"), new_directory=new_dir
    )
    assert all(item.prefix == "new_prefix" for item in new_sequence.items)
    assert all(item.directory == new_dir for item in new_sequence.items)

    # Assert original sequence hasn't changed (frozen)
    assert all(item.directory == original_dir for item in sequence.items)
    assert all(item.prefix == "test" for item in sequence.items)

    # Assert original files still exist and no new files created
    assert all(f.exists() for f in files)
    assert not new_dir.exists() or not any(
        (new_dir / f.name).exists() for f in files
    )
    assert not any(
        (original_dir / f"test_copy.{i:04d}.exr").exists() for i in range(1001, 1004)
    )
    assert not any(
        (original_dir / f"new_prefix.{i:04d}.exr").exists() for i in range(1001, 1004)
    )

    # Test that frame numbers and other properties are preserved
    for orig_item, new_item in zip(sequence.items, new_sequence.items):
        assert new_item.frame_number == orig_item.frame_number
        assert new_item.extension == orig_item.extension
        assert new_item.padding == orig_item.padding
