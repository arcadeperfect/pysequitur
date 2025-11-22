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

    # Create sequence
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test offset with no collisions (offset to unused frame range)
    offset_sequence = sequence.offset_frames(100)  # 1001-1003 -> 1101-1103

    # Should succeed and return the same sequence
    assert offset_sequence is sequence

    # Assert files are renamed to new frame numbers
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1101, 1104))
    assert not any(
        (original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004)
    )

    # Assert frame numbers are updated in sequence
    assert all(
        item.frame_number == i for item, i in zip(sequence.items, range(1101, 1104))
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test offset that would collide with existing files
    with pytest.raises(FileExistsError) as exc_info:
        sequence.offset_frames(10)  # 1001-1003 -> 1011-1013 (conflicts!)

    # Check error message contains conflict information
    error_msg = str(exc_info.value)
    assert "Offset would create conflicts with existing files" in error_msg
    assert "test.1011.exr" in error_msg
    assert "test.1012.exr" in error_msg
    assert "test.1013.exr" in error_msg

    # Assert original files are unchanged (operation was aborted)
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))
    assert all(
        item.frame_number == i for item, i in zip(sequence.items, range(1001, 1004))
    )

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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test offset that would partially collide
    with pytest.raises(FileExistsError) as exc_info:
        sequence.offset_frames(10)  # 1001-1003 -> 1011-1013, but 1012 exists

    # Check error message mentions the conflicting file
    error_msg = str(exc_info.value)
    assert "test.1012.exr" in error_msg
    # Should not mention non-conflicting files
    assert "test.1011.exr" not in error_msg
    assert "test.1013.exr" not in error_msg

    # Assert original files are unchanged
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))


def test_offset_frames_internal_collision_avoidance(tmp_path):
    """Test that offset_frames avoids internal collisions by processing in correct order."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence where offset will definitely cause internal collision
    # Using consecutive frames [1001, 1002] with offset +1:
    # Processing order (reverse for positive offset): [1002, 1001]
    # 1002 -> 1003 (no collision)
    # 1001 -> 1002 (collision with original 1002, but 1002 was already moved to 1003)
    # Let's try a different approach: [1001, 1003] with offset -2
    # Processing order (normal for negative offset): [1001, 1003]
    # 1001 -> 999 (no collision)
    # 1003 -> 1001 (collision with original 1001, but 1001 was moved to 999)

    # Actually, let's test the behavior rather than assume collision
    # Create a simple consecutive sequence
    frame_numbers = [1001, 1002]
    files = []
    for i in frame_numbers:
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create sequence
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test offset - this should actually succeed because the algorithm
    # processes items in an order that avoids internal collisions
    result = sequence.offset_frames(1)  # 1001->1002, 1002->1003

    # The algorithm is designed to avoid internal collisions by processing
    # in the right order, so this should succeed
    assert result is sequence

    # Verify the frames were offset correctly
    expected_frames = [1002, 1003]
    actual_frames = sorted([item.frame_number for item in sequence.items])
    assert actual_frames == expected_frames


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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Verify sequence only has 2 items (1000, 1002)
    assert len(sequence.items) == 2
    assert sorted([item.frame_number for item in sequence.items]) == [1000, 1002]

    # Now offset by +1: 1000->1001 (external collision!), 1002->1003 (ok)
    # This should be caught by our NEW external collision detection
    with pytest.raises(FileExistsError) as exc_info:
        sequence.offset_frames(1)

    # Should be external collision error (our new feature)
    assert "Offset would create conflicts with existing files" in str(exc_info.value)
    assert "test.1001.exr" in str(exc_info.value)


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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test offset - should succeed because extensions are different
    offset_sequence = sequence.offset_frames(10)  # 1001-1003 -> 1011-1013

    # Should succeed (no collision due to different extensions)
    assert offset_sequence is sequence
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test offset - should succeed because prefixes are different
    offset_sequence = sequence.offset_frames(10)  # 1001-1003 -> 1011-1013

    # Should succeed (no collision due to different prefixes)
    assert offset_sequence is sequence
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1011, 1014))


def test_offset_frames_collision_virtual_mode_ignores_conflicts(tmp_path):
    """Test that virtual mode ignores collision detection."""
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test virtual offset - should succeed despite conflicts
    virtual_sequence = sequence.offset_frames(10, virtual=True)

    # Should return new sequence (virtual mode)
    assert virtual_sequence is not sequence
    assert len(virtual_sequence.items) == 3

    # Virtual sequence should have updated frame numbers
    assert all(
        item.frame_number == i
        for item, i in zip(virtual_sequence.items, range(1011, 1014))
    )

    # Original files should be unchanged
    assert all((original_dir / f"test.{i:04d}.exr").exists() for i in range(1001, 1004))
    assert all(
        item.frame_number == i for item, i in zip(sequence.items, range(1001, 1004))
    )


def test_offset_frames_zero_offset_no_collision_check(tmp_path):
    """Test that zero offset bypasses collision detection."""
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

    # Test zero offset - should return immediately without collision checking
    result = sequence.offset_frames(0)

    # Should return the same sequence unchanged
    assert result is sequence
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

    # Create conflicting file with different padding (3-digit)
    conflict_file = (
        original_dir / f"test.{1011:03d}.exr"
    )  # "test.1011.exr" vs "test.1011.exr"
    conflict_file.touch()

    # Create sequence
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test offset with custom padding that would match the conflict
    with pytest.raises(FileExistsError):
        sequence.offset_frames(
            10, padding=3
        )  # Would create "test.1011.exr" which exists


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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test offset and check error message format
    with pytest.raises(FileExistsError) as exc_info:
        sequence.offset_frames(10)

    error_msg = str(exc_info.value)

    # Check error message structure
    assert error_msg.startswith("Offset would create conflicts with existing files:")
    assert str(original_dir / "test.1011.exr") in error_msg
    assert str(original_dir / "test.1012.exr") in error_msg

    # Should be a list format
    assert "[" in error_msg and "]" in error_msg
