import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_move_conflict_detection_and_error_handling(tmp_path):
    """Test that move properly detects conflicts and raises appropriate errors."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting files in target directory
    conflicting_files = []
    for i in range(1001, 1004):
        conflict_file = target_dir / f"test.{i:04d}.exr"
        conflict_file.touch()
        conflicting_files.append(conflict_file)

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get move plan
    new_sequence, plan = sequence.move(target_dir)

    # Verify conflicts are detected
    assert plan.has_conflicts
    assert len(plan.conflicts) == 3

    # Test that execute detects conflicts and raises FileExistsError
    with pytest.raises(FileExistsError) as exc_info:
        plan.execute()

    # Validate error message format
    error_msg = str(exc_info.value)
    assert "Conflicts" in error_msg

    # Verify original files are unchanged after failed move
    assert all(f.exists() for f in files)

    # Verify conflicting files still exist
    assert all(cf.exists() for cf in conflicting_files)


def test_move_partial_conflict_detection(tmp_path):
    """Test move with partial conflicts (some files conflict, others don't)."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting file for only one frame
    conflict_file = target_dir / "test.1002.exr"
    conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get move plan
    new_sequence, plan = sequence.move(target_dir)

    # Verify partial conflict is detected
    assert plan.has_conflicts
    assert len(plan.conflicts) == 1

    # Execute should fail
    with pytest.raises(FileExistsError):
        plan.execute()

    # Verify no files were moved (atomic failure before execution)
    assert all(f.exists() for f in files)


def test_move_same_directory_optimization(tmp_path):
    """Test that moving to the same directory is optimized (no-op)."""
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

    # Test move to same directory - should be a no-op
    new_sequence, plan = sequence.move(original_dir)

    # Should be empty plan
    assert len(plan.operations) == 0
    assert not plan.has_conflicts

    # Files should still exist in original location
    assert all(f.exists() for f in files)


def test_move_conflict_detection_with_different_extensions(tmp_path):
    """Test that conflict detection respects file extensions."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # Create a sequence of .exr files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create files with same names but different extensions in target
    for i in range(1001, 1004):
        different_ext_file = target_dir / f"test.{i:04d}.jpg"
        different_ext_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get move plan - should succeed because extensions are different
    new_sequence, plan = sequence.move(target_dir)

    # No conflicts
    assert not plan.has_conflicts

    # Execute
    plan.execute()

    # Files should exist in target with .exr extension
    assert all((target_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))

    # Original .jpg files should still exist
    assert all((target_dir / f"test.{i:04d}.jpg").exists() for i in range(1001, 1004))

    # Original files should be gone
    assert not any(f.exists() for f in files)


def test_move_conflict_detection_with_different_prefixes(tmp_path):
    """Test that conflict detection respects filename prefixes."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # Create a sequence with "test" prefix
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create files with different prefix in target
    for i in range(1001, 1004):
        different_prefix_file = target_dir / f"render.{i:04d}.exr"
        different_prefix_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get move plan - should succeed because prefixes are different
    new_sequence, plan = sequence.move(target_dir)

    # No conflicts
    assert not plan.has_conflicts

    # Execute
    plan.execute()

    # Files should exist in target with "test" prefix
    assert all((target_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))

    # Original "render" files should still exist
    assert all((target_dir / f"render.{i:04d}.exr").exists() for i in range(1001, 1004))

    # Original files should be gone
    assert not any(f.exists() for f in files)


def test_move_error_message_format_validation(tmp_path):
    """Test that move conflict error messages are properly formatted."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1003):  # Just 2 files for simpler testing
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting files
    for i in range(1001, 1003):
        conflict_file = target_dir / f"test.{i:04d}.exr"
        conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get move plan and try to execute
    new_sequence, plan = sequence.move(target_dir)

    with pytest.raises(FileExistsError) as exc_info:
        plan.execute()

    error_msg = str(exc_info.value)

    # Check error message structure
    assert "Conflicts" in error_msg


def test_move_atomic_failure_behavior(tmp_path):
    """Test that move operations fail atomically (all or nothing)."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1005):  # 4 files
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting file for only the last frame
    conflict_file = target_dir / "test.1004.exr"
    conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get move plan
    new_sequence, plan = sequence.move(target_dir)

    # Should have conflict
    assert plan.has_conflicts

    # Execute should fail
    with pytest.raises(FileExistsError):
        plan.execute()

    # Verify atomic failure: NO files should have been moved
    # All original files should still exist
    assert all(f.exists() for f in files)

    # No files should exist in target (except the original conflict)
    moved_files = [target_dir / f"test.{i:04d}.exr" for i in range(1001, 1004)]
    assert not any(f.exists() for f in moved_files)

    # Only the original conflicting file should exist in target
    assert conflict_file.exists()


def test_move_successful_operation_validation(tmp_path):
    """Test that successful move operations work correctly."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Store original frame numbers for validation
    original_frames = [item.frame_number for item in sequence.items]

    # Test successful move
    new_sequence, plan = sequence.move(target_dir)

    # No conflicts
    assert not plan.has_conflicts

    # Execute
    plan.execute()

    # New sequence is a separate object
    assert new_sequence is not sequence

    # Files should exist in target directory
    target_files = [target_dir / f"test.{i:04d}.exr" for i in range(1001, 1004)]
    assert all(f.exists() for f in target_files)

    # Original files should be gone
    assert not any(f.exists() for f in files)

    # New sequence should point to new directory
    assert all(item.directory == target_dir for item in new_sequence.items)

    # Frame numbers and other properties should be preserved
    assert [item.frame_number for item in new_sequence.items] == original_frames
    assert all(item.prefix == "test" for item in new_sequence.items)
    assert all(item.extension == "exr" for item in new_sequence.items)


def test_move_nonexistent_directory_behavior(tmp_path):
    """Test move behavior with non-existent target directories."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    target_dir = tmp_path / "nonexistent"  # Don't create this

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test move to non-existent directory without create_directory flag
    new_sequence, plan = sequence.move(target_dir)

    # Execute should fail (directory doesn't exist)
    result = plan.execute()
    assert len(result.failed) > 0

    # Test move with create_directory flag - should succeed
    new_sequence, plan = sequence.move(target_dir, create_directory=True)
    plan.execute()

    # Should succeed
    assert target_dir.exists()
    assert all((target_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))
    assert not any(f.exists() for f in files)
