import pytest
from pathlib import Path
from pysequitur import Item, FileSequence
from pysequitur.file_sequence import Components


def test_file_sequence_delete_basic_operation(tmp_path):
    """Test basic delete operation."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files with content
    files = []
    original_contents = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        content = f"test content {i}"
        test_file.write_text(content)
        files.append(test_file)
        original_contents.append(content)

    # Create sequence (now uses tuple)
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Verify files exist before deletion
    assert all(f.exists() for f in files)
    assert all(item.exists for item in sequence.items)

    # Get delete plan and execute
    plan = sequence.delete()
    plan.execute()

    # All files should be deleted
    assert all(not f.exists() for f in files)
    assert all(not item.exists for item in sequence.items)


def test_file_sequence_delete_nonexistent_files(tmp_path):
    """Test delete behavior with nonexistent files."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create sequence items that reference nonexistent files
    items = []
    for i in range(1001, 1004):
        item = Item.from_file_name(f"test.{i:04d}.exr", original_dir)
        items.append(item)

    sequence = FileSequence(tuple(items))

    # Verify files don't exist
    assert all(not item.exists for item in sequence.items)

    # delete should fail on execute for nonexistent files
    plan = sequence.delete()
    result = plan.execute()
    
    # Should have failures
    assert len(result.failed) > 0


def test_file_sequence_delete_partial_existence(tmp_path):
    """Test delete behavior when only some files exist."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create some files but not others
    files_to_create = [1001, 1003]  # Skip 1002
    existing_files = []

    for i in files_to_create:
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.write_text(f"content {i}")
        existing_files.append(test_file)

    # Create sequence with all three items (including nonexistent 1002)
    items = []
    for i in range(1001, 1004):
        item = Item.from_file_name(f"test.{i:04d}.exr", original_dir)
        items.append(item)

    sequence = FileSequence(tuple(items))

    # Verify partial existence
    assert sequence.items[0].exists  # 1001 exists
    assert not sequence.items[1].exists  # 1002 doesn't exist
    assert sequence.items[2].exists  # 1003 exists

    # Get delete plan and execute
    plan = sequence.delete()
    result = plan.execute()

    # Some operations will fail
    assert len(result.failed) > 0

    # Files that existed should be deleted
    assert not existing_files[0].exists()  # 1001 was deleted
    # 1003 was also deleted
    assert not existing_files[1].exists()


def test_file_sequence_delete_empty_sequence():
    """Test delete with empty sequence."""
    # Create empty sequence
    sequence = FileSequence(())

    # Should succeed without error
    plan = sequence.delete()
    result = plan.execute()

    # Should succeed
    assert result.success
    assert len(plan.operations) == 0


def test_file_sequence_delete_single_file(tmp_path):
    """Test delete with single file sequence."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create single file
    test_file = original_dir / "test.1001.exr"
    test_file.write_text("single file content")

    # Create sequence
    item = Item.from_path(test_file)
    sequence = FileSequence((item,))

    # Verify file exists
    assert test_file.exists()
    assert item.exists

    # Delete
    plan = sequence.delete()
    result = plan.execute()

    # Should succeed
    assert result.success
    assert not test_file.exists()
    assert not item.exists


def test_file_sequence_delete_preserves_sequence_structure(tmp_path):
    """Test that delete preserves sequence structure after deletion."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.write_text(f"content {i}")
        files.append(test_file)

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Store original sequence properties
    original_prefix = sequence.prefix
    original_extension = sequence.extension
    original_frame_count = len(sequence.items)
    original_first_frame = sequence.first_frame
    original_last_frame = sequence.last_frame

    # Delete files
    plan = sequence.delete()
    plan.execute()

    # Sequence structure should be preserved (frozen)
    assert sequence.prefix == original_prefix
    assert sequence.extension == original_extension
    assert len(sequence.items) == original_frame_count
    assert sequence.first_frame == original_first_frame
    assert sequence.last_frame == original_last_frame

    # Only the file existence should change
    assert all(not item.exists for item in sequence.items)


def test_file_sequence_delete_large_sequence(tmp_path):
    """Test delete with larger sequence to check performance/reliability."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create larger sequence (50 files)
    files = []
    for i in range(1001, 1051):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.write_text(f"content {i}")
        files.append(test_file)

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Verify all files exist
    assert len(sequence.items) == 50
    assert all(item.exists for item in sequence.items)

    # Delete all files
    plan = sequence.delete()
    result = plan.execute()

    # Should succeed
    assert result.success
    assert all(not f.exists() for f in files)
    assert all(not item.exists for item in sequence.items)
