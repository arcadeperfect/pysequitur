import pytest

from pysequitur import FileSequence, Item


def test_offset_frames_no_collisions(tmp_path):
    """Test offset_frames when no collisions exist."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create sequence (using tuple for frozen dataclass)
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test offset with no collisions (offset to unused frame range)
    offset_sequence, plan = sequence.offset_frames(100)  # 1001-1003 -> 1101-1103

    # Should return new sequence (frozen dataclass)
    assert offset_sequence is not sequence
    assert not plan.has_conflicts

    # Execute the plan
    plan.execute()

    # Assert files are renamed to new frame numbers
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1101, 1104))
    assert not any(
        (original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004)
    )

    # Assert frame numbers are updated in new sequence
    assert all(
        item.frame_number == i
        for item, i in zip(offset_sequence.items, range(1101, 1104))
    )


def test_offset_frames_with_external_collisions(tmp_path):
    """Test offset_frames when target frames conflict with existing external files."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files (1001-1003)
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting files at target locations (1011-1013)
    conflicting_files = []
    for i in range(1011, 1014):
        conflict_file = original_dir / f"test.{i:04d}.exr"
        conflict_file.touch()
        conflicting_files.append(conflict_file)

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test offset that would collide with existing files
    offset_sequence, plan = sequence.offset_frames(10)  # 1001-1003 -> 1011-1013

    # Plan should detect conflicts
    assert plan.has_conflicts
    assert len(plan.conflicts) == 3

    # Executing should raise FileExistsError
    with pytest.raises(FileExistsError) as exc_info:
        plan.execute()

    # Check error message contains conflict information
    error_msg = str(exc_info.value)
    assert "Conflicts" in error_msg

    # Assert original files are unchanged (operation was aborted)
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))

    # Assert conflicting files still exist
    assert all(conflict_file.exists() for conflict_file in conflicting_files)


def test_offset_frames_partial_collisions(tmp_path):
    """Test offset_frames when only some target frames conflict."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files (1001-1003)
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting file for only the middle target frame
    conflict_file = original_dir / "test.1012.exr"  # Only 1012 conflicts
    conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test offset that would partially collide
    offset_sequence, plan = sequence.offset_frames(10)  # 1001-1003 -> 1011-1013

    # Plan should detect partial conflict
    assert plan.has_conflicts
    assert len(plan.conflicts) == 1

    # Executing should raise FileExistsError
    with pytest.raises(FileExistsError):
        plan.execute()

    # Assert original files are unchanged
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))


def test_offset_frames_internal_collision_avoidance(tmp_path):
    """Test that offset_frames handles internal collisions correctly.
    
    When offsetting consecutive frames, the plan will detect an "internal collision"
    (target file exists because it's one of our source files). The execution handles
    this by processing files in the correct order (high to low for positive offsets).
    """
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a simple consecutive sequence
    frame_numbers = [1001, 1002]
    files = []
    for i in frame_numbers:
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test offset: 1001->1002, 1002->1003
    # The plan detects "test.1002.exr" as a conflict (it exists as source file)
    new_sequence, plan = sequence.offset_frames(1)

    # Should return new sequence (frozen)
    assert new_sequence is not sequence
    
    # Plan shows internal collision as conflict
    # (target 1002 exists because it's one of our source files)
    assert plan.has_conflicts
    assert len(plan.conflicts) == 1

    # Execute with force=True to handle internal collisions
    # The execution order (1002->1003 first, then 1001->1002) ensures correctness
    result = plan.execute(force=True)

    # Should succeed
    assert result.success

    # Verify the frames were offset correctly
    expected_frames = [1002, 1003]
    actual_frames = sorted([item.frame_number for item in new_sequence.items])
    assert actual_frames == expected_frames

    # Verify files exist at new locations
    assert (original_dir / "test.1002.exr").exists()
    assert (original_dir / "test.1003.exr").exists()
    # Original 1001 should be gone
    assert not (original_dir / "test.1001.exr").exists()


def test_offset_frames_demonstrates_external_vs_internal_collision(tmp_path):
    """Test that demonstrates the difference between external and internal collision detection."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence
    frame_numbers = [1000, 1002]
    files = []
    for i in frame_numbers:
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create an external collision target
    collision_file = original_dir / "test.1001.exr"
    collision_file.touch()

    # Create sequence (should only include 1000 and 1002, not 1001)
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Verify sequence only has 2 items (1000, 1002)
    assert len(sequence.items) == 2
    assert sorted([item.frame_number for item in sequence.items]) == [1000, 1002]

    # Now offset by +1: 1000->1001 (external collision!), 1002->1003 (ok)
    new_sequence, plan = sequence.offset_frames(1)

    # Plan should detect the external collision
    assert plan.has_conflicts
    assert len(plan.conflicts) == 1

    # Executing should raise FileExistsError
    with pytest.raises(FileExistsError):
        plan.execute()


def test_offset_frames_collision_with_different_extensions(tmp_path):
    """Test that collision detection respects file extensions."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of .exr files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting files with different extension (.jpg)
    for i in range(1011, 1014):
        conflict_file = original_dir / f"test.{i:04d}.jpg"
        conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test offset - should succeed because extensions are different
    offset_sequence, plan = sequence.offset_frames(10)  # 1001-1003 -> 1011-1013

    # Should return new sequence (frozen)
    assert offset_sequence is not sequence
    # Should not have conflicts due to different extensions
    assert not plan.has_conflicts

    # Execute and verify
    plan.execute()
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1011, 1014))


def test_offset_frames_collision_with_different_prefix(tmp_path):
    """Test that collision detection respects filename prefixes."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files with "test" prefix
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting files with different prefix
    for i in range(1011, 1014):
        conflict_file = original_dir / f"render.{i:04d}.exr"
        conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test offset - should succeed because prefixes are different
    offset_sequence, plan = sequence.offset_frames(10)  # 1001-1003 -> 1011-1013

    # Should return new sequence (frozen)
    assert offset_sequence is not sequence
    # Should not have conflicts due to different prefixes
    assert not plan.has_conflicts

    # Execute and verify
    plan.execute()
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1011, 1014))


def test_offset_frames_without_execute_ignores_filesystem(tmp_path):
    """Test that offset_frames without execute doesn't modify filesystem."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting files at target locations
    for i in range(1011, 1014):
        conflict_file = original_dir / f"test.{i:04d}.exr"
        conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get plan without executing - conflicts exist but plan is still created
    new_sequence, plan = sequence.offset_frames(10)

    # New sequence represents the proposed state
    assert new_sequence is not sequence
    assert len(new_sequence.items) == 3

    # New sequence should have updated frame numbers
    assert all(
        item.frame_number == i
        for item, i in zip(new_sequence.items, range(1011, 1014))
    )

    # Original files should be unchanged (we didn't execute)
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))

    # Original sequence is unchanged (frozen)
    assert all(
        item.frame_number == i for item, i in zip(sequence.items, range(1001, 1004))
    )


def test_offset_frames_zero_offset_returns_empty_plan(tmp_path):
    """Test that zero offset returns empty plan."""
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

    # Test zero offset - should return same sequence with empty plan
    result_sequence, plan = sequence.offset_frames(0)

    # For zero offset, same sequence is returned
    assert result_sequence is sequence
    # Empty plan (no operations needed)
    assert len(plan.operations) == 0
    assert not plan.has_conflicts

    # Frame numbers unchanged
    assert all(
        item.frame_number == i for item, i in zip(sequence.items, range(1001, 1004))
    )


def test_offset_frames_collision_with_padding_differences(tmp_path):
    """Test collision detection with different padding lengths."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence with 4-digit padding
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting file with 3-digit padding at target location
    # When we offset with padding=3, "1011" would become "test.1011.exr"
    conflict_file = original_dir / "test.1011.exr"
    conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test offset with custom padding that would match the conflict
    new_sequence, plan = sequence.offset_frames(10, padding=3)

    # Plan should detect the conflict
    assert plan.has_conflicts

    # Executing should raise
    with pytest.raises(FileExistsError):
        plan.execute()


def test_offset_frames_collision_error_message_format(tmp_path):
    """Test that collision error messages are properly formatted."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1003):  # Just 2 files for simpler testing
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting files
    for i in range(1011, 1013):
        conflict_file = original_dir / f"test.{i:04d}.exr"
        conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get plan and verify conflicts
    new_sequence, plan = sequence.offset_frames(10)
    assert plan.has_conflicts
    assert len(plan.conflicts) == 2

    # Execute should raise with error message
    with pytest.raises(FileExistsError) as exc_info:
        plan.execute()

    error_msg = str(exc_info.value)

    # Check error message structure
    assert "Conflicts" in error_msg
