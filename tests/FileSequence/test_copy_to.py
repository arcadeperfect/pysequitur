import pytest
from pathlib import Path
from pysequitur import Item, FileSequence
from pysequitur.file_sequence import Components


def test_file_sequence_copy_to(tmp_path):
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

    # Test copy to non-existent directory without create_directory flag
    new_dir = tmp_path / "new"
    with pytest.raises(FileNotFoundError):
        sequence.copy_to(new_directory=new_dir)

    # Test copy with create_directory flag
    copied_sequence = sequence.copy_to(new_directory=new_dir, create_directory=True)

    # Assert copied_sequence is a new instance
    assert copied_sequence is not sequence

    # Assert copied files exist in new location
    assert all((new_dir / f.name).exists() for f in files)
    # Assert original files still exist
    assert all(f.exists() for f in files)

    # Test copy with default settings (should add '_copy' to prefix)
    copied_sequence = (
        sequence.copy_to()
    )  # No need for create_directory as using same dir
    assert all(
        (original_dir / f"test_copy.{i:04d}.exr").exists() for i in range(1001, 1004)
    )
    assert all(item.prefix == "test_copy" for item in copied_sequence.items)

    # Clean up copied files
    for i in range(1001, 1004):
        (original_dir / f"test_copy.{i:04d}.exr").unlink()

    # Test copy with new Components
    copied_sequence = sequence.copy_to(Components(prefix="new_prefix"))
    assert all(
        (original_dir / f"new_prefix.{i:04d}.exr").exists() for i in range(1001, 1004)
    )
    assert all(item.prefix == "new_prefix" for item in copied_sequence.items)

    # Clean up copied files
    for i in range(1001, 1004):
        (original_dir / f"new_prefix.{i:04d}.exr").unlink()

    # Test copy with both new directory and Components to nested non-existent directory
    nested_dir = tmp_path / "nested" / "path"
    with pytest.raises(FileNotFoundError):
        sequence.copy_to(Components(prefix="new_prefix"), new_directory=nested_dir)

    # Now test with create_directory flag
    copied_sequence = sequence.copy_to(
        Components(prefix="new_prefix"), new_directory=nested_dir, create_directory=True
    )
    assert all(
        (nested_dir / f"new_prefix.{i:04d}.exr").exists() for i in range(1001, 1004)
    )
    assert all(item.prefix == "new_prefix" for item in copied_sequence.items)
    assert all(item.directory == nested_dir for item in copied_sequence.items)

    # Assert original sequence hasn't changed
    assert all(item.directory == original_dir for item in sequence.items)
    assert all(item.prefix == "test" for item in sequence.items)
    assert all(f.exists() for f in files)

    # Test that frame numbers and other properties are preserved
    for orig_item, copied_item in zip(sequence.items, copied_sequence.items):
        assert copied_item.frame_number == orig_item.frame_number
        assert copied_item.extension == orig_item.extension
        assert copied_item.padding == orig_item.padding
