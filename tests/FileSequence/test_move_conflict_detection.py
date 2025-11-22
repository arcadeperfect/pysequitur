import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_move_to_conflict_detection_and_error_handling(tmp_path):
    """Test that move_to properly detects conflicts and raises appropriate errors."""
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test that move_to detects conflicts and raises FileExistsError
    with pytest.raises(FileExistsError) as exc_info:
        sequence.move_to(target_dir)

    # Validate error message format
    error_msg = str(exc_info.value)
    assert "Conflicts detected:" in error_msg
    
    # Should mention the conflicting files
    for conflict_file in conflicting_files:
        assert str(conflict_file) in error_msg

    # Verify original files are unchanged after failed move
    assert all(f.exists() for f in files)
    assert all(item.directory == original_dir for item in sequence.items)
    
    # Verify conflicting files still exist
    assert all(cf.exists() for cf in conflicting_files)


def test_move_to_partial_conflict_detection(tmp_path):
    """Test move_to with partial conflicts (some files conflict, others don't)."""
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test that move_to detects partial conflict and fails
    with pytest.raises(FileExistsError) as exc_info:
        sequence.move_to(target_dir)

    # Should mention the conflicting file
    error_msg = str(exc_info.value)
    assert str(conflict_file) in error_msg
    
    # Should not mention non-conflicting files in error
    non_conflicting = [target_dir / "test.1001.exr", target_dir / "test.1003.exr"]
    for non_conflict in non_conflicting:
        assert str(non_conflict) not in error_msg

    # Verify no files were moved (atomic failure)
    assert all(f.exists() for f in files)
    assert all(item.directory == original_dir for item in sequence.items)


def test_move_to_same_directory_optimization(tmp_path):
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test move to same directory - should be a no-op
    result = sequence.move_to(original_dir)

    # Should return the same sequence
    assert result is sequence
    
    # Files should still exist in original location
    assert all(f.exists() for f in files)
    assert all(item.directory == original_dir for item in sequence.items)


def test_move_to_conflict_detection_with_different_extensions(tmp_path):
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test move - should succeed because extensions are different
    result = sequence.move_to(target_dir)

    # Should succeed
    assert result is sequence
    
    # Files should exist in target with .exr extension
    assert all((target_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))
    
    # Original .jpg files should still exist
    assert all((target_dir / f"test.{i:04d}.jpg").exists() for i in range(1001, 1004))
    
    # Original files should be gone
    assert not any(f.exists() for f in files)


def test_move_to_conflict_detection_with_different_prefixes(tmp_path):
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test move - should succeed because prefixes are different
    result = sequence.move_to(target_dir)

    # Should succeed
    assert result is sequence
    
    # Files should exist in target with "test" prefix
    assert all((target_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))
    
    # Original "render" files should still exist
    assert all((target_dir / f"render.{i:04d}.exr").exists() for i in range(1001, 1004))
    
    # Original files should be gone
    assert not any(f.exists() for f in files)


def test_move_to_error_message_format_validation(tmp_path):
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
    conflicting_files = []
    for i in range(1001, 1003):
        conflict_file = target_dir / f"test.{i:04d}.exr"
        conflict_file.touch()
        conflicting_files.append(conflict_file)

    # Create sequence
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test move and check error message format
    with pytest.raises(FileExistsError) as exc_info:
        sequence.move_to(target_dir)

    error_msg = str(exc_info.value)
    
    # Check error message structure
    assert error_msg.startswith("Conflicts detected:")
    
    # Should contain all conflicting file paths
    for conflict_file in conflicting_files:
        assert str(conflict_file) in error_msg
    
    # Should be a list format
    assert "[" in error_msg and "]" in error_msg


def test_move_to_atomic_failure_behavior(tmp_path):
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test move - should fail due to conflict with last file
    with pytest.raises(FileExistsError):
        sequence.move_to(target_dir)

    # Verify atomic failure: NO files should have been moved
    # All original files should still exist
    assert all(f.exists() for f in files)
    
    # No files should exist in target (except the original conflict)
    moved_files = [target_dir / f"test.{i:04d}.exr" for i in range(1001, 1004)]
    assert not any(f.exists() for f in moved_files)
    
    # Only the original conflicting file should exist in target
    assert conflict_file.exists()
    
    # Sequence should still point to original directory
    assert all(item.directory == original_dir for item in sequence.items)


def test_move_to_successful_operation_validation(tmp_path):
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Store original frame numbers for validation
    original_frames = [item.frame_number for item in sequence.items]

    # Test successful move
    result = sequence.move_to(target_dir)

    # Should return the same sequence (modified in place)
    assert result is sequence
    
    # Files should exist in target directory
    target_files = [target_dir / f"test.{i:04d}.exr" for i in range(1001, 1004)]
    assert all(f.exists() for f in target_files)
    
    # Original files should be gone
    assert not any(f.exists() for f in files)
    
    # Sequence should point to new directory
    assert all(item.directory == target_dir for item in sequence.items)
    
    # Frame numbers and other properties should be preserved
    assert [item.frame_number for item in sequence.items] == original_frames
    assert all(item.prefix == "test" for item in sequence.items)
    assert all(item.extension == "exr" for item in sequence.items)


def test_move_to_nonexistent_directory_behavior(tmp_path):
    """Test move_to behavior with non-existent target directories."""
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test move to non-existent directory without create_directory flag
    with pytest.raises(FileNotFoundError):
        sequence.move_to(target_dir)

    # Files should still exist in original location
    assert all(f.exists() for f in files)
    assert all(item.directory == original_dir for item in sequence.items)

    # Test move with create_directory flag - should succeed
    result = sequence.move_to(target_dir, create_directory=True)

    # Should succeed
    assert result is sequence
    assert target_dir.exists()
    assert all((target_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))
    assert not any(f.exists() for f in files)
