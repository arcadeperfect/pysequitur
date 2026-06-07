import pytest
from pathlib import Path
from pysequitur import Item, FileSequence
from pysequitur.file_sequence import Components


def test_file_sequence_rename_conflict_detection(tmp_path):
    """Test that rename properly detects and prevents conflicts."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting files
    for i in range(1001, 1004):
        conflict_file = original_dir / f"new_prefix.{i:04d}.exr"
        conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get rename plan
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.rename(new_components)

    # Verify conflicts detected
    assert plan.has_conflicts
    assert len(plan.conflicts) == 3

    # Attempt execute should fail due to conflicts
    with pytest.raises(FileExistsError):
        plan.execute()

    # Original files should still exist and be unchanged
    assert all(f.exists() for f in files)


def test_file_sequence_rename_partial_conflicts(tmp_path):
    """Test rename behavior with partial conflicts."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting file for only one frame
    conflict_file = original_dir / "new_prefix.1002.exr"
    conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get rename plan
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.rename(new_components)

    # Verify partial conflict detected
    assert plan.has_conflicts
    assert len(plan.conflicts) == 1

    # Execute should fail
    with pytest.raises(FileExistsError):
        plan.execute()

    # All original files should still exist (atomic failure)
    assert all(f.exists() for f in files)


def test_file_sequence_rename_different_extensions_no_conflict(tmp_path):
    """Test rename with different extensions (should not conflict)."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of .exr files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create files with same names but different extensions
    for i in range(1001, 1004):
        different_ext_file = original_dir / f"test.{i:04d}.jpg"
        different_ext_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Rename to change prefix (should succeed, different extensions)
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.rename(new_components)

    # No conflicts
    assert not plan.has_conflicts

    # Execute
    plan.execute()

    # Check that files were renamed
    for i in range(1001, 1004):
        new_file = original_dir / f"new_prefix.{i:04d}.exr"
        assert new_file.exists()

        # Original files should no longer exist
        old_file = original_dir / f"test.{i:04d}.exr"
        assert not old_file.exists()


def test_file_sequence_rename_different_prefixes_no_conflict(tmp_path):
    """Test rename with different prefixes (should not conflict)."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create files with different prefix
    for i in range(1001, 1004):
        different_prefix_file = original_dir / f"other.{i:04d}.exr"
        different_prefix_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Rename to new prefix (should succeed)
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.rename(new_components)

    # No conflicts
    assert not plan.has_conflicts

    # Execute
    plan.execute()

    # Check that files were renamed
    for i in range(1001, 1004):
        new_file = original_dir / f"new_prefix.{i:04d}.exr"
        assert new_file.exists()


def test_file_sequence_rename_error_message_format(tmp_path):
    """Test that rename error messages are informative."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1003):  # Just 2 files for simpler error message
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting files
    for i in range(1001, 1003):
        conflict_file = original_dir / f"new_prefix.{i:04d}.exr"
        conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get rename plan and try to execute
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.rename(new_components)

    # Should have conflicts
    assert plan.has_conflicts

    with pytest.raises(FileExistsError) as exc_info:
        plan.execute()

    error_msg = str(exc_info.value)

    # Error should mention conflicts
    assert "Conflicts" in error_msg


def test_file_sequence_rename_atomic_failure(tmp_path):
    """Test that rename fails atomically (all or nothing)."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting file for only the last frame
    conflict_file = original_dir / "new_prefix.1003.exr"
    conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get rename plan
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.rename(new_components)

    # Should have conflict
    assert plan.has_conflicts

    # Execute should fail
    with pytest.raises(FileExistsError):
        plan.execute()

    # ALL original files should still exist (atomic failure)
    assert all(f.exists() for f in files)

    # NO new files should have been created
    for i in range(1001, 1003):  # First two frames
        new_file = original_dir / f"new_prefix.{i:04d}.exr"
        assert not new_file.exists()


def test_file_sequence_rename_successful_operation(tmp_path):
    """Test successful rename operation."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    original_contents = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        content = f"test content {i}"
        test_file.write_text(content)
        files.append(test_file)
        original_contents.append(content)

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Perform successful rename
    new_components = Components(prefix="renamed")
    new_sequence, plan = sequence.rename(new_components)

    # No conflicts
    assert not plan.has_conflicts

    # Execute
    plan.execute()

    # Check that new files exist with correct content
    for i, content in enumerate(original_contents):
        frame_num = 1001 + i
        new_file = original_dir / f"renamed.{frame_num:04d}.exr"
        assert new_file.exists()
        assert new_file.read_text() == content

        # Original files should no longer exist
        old_file = original_dir / f"test.{frame_num:04d}.exr"
        assert not old_file.exists()

    # New sequence should have correct prefix
    assert all(item.prefix == "renamed" for item in new_sequence.items)


def test_file_sequence_rename_empty_sequence():
    """Test rename with empty sequence."""
    # Create empty sequence
    sequence = FileSequence(())

    # Should succeed without error
    new_components = Components(prefix="new_name")
    new_sequence, plan = sequence.rename(new_components)

    # Empty plan
    assert len(plan.operations) == 0
    assert not plan.has_conflicts


def test_file_sequence_rename_self_collision_detection(tmp_path):
    """Test rename detects self-collision (renaming to same name)."""
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
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Attempt to rename to the same name - should be empty plan
    new_components = Components(prefix="test")  # Same as current
    new_sequence, plan = sequence.rename(new_components)

    # Should be empty plan (no changes needed)
    assert len(plan.operations) == 0
    assert not plan.has_conflicts

    # Files should remain unchanged
    assert all(f.exists() for f in files)
