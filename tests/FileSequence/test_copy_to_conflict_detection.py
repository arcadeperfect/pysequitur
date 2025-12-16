import pytest
from pathlib import Path
from pysequitur import Item, FileSequence
from pysequitur.file_sequence import Components


def test_file_sequence_copy_conflict_detection(tmp_path):
    """Test that copy properly detects and prevents conflicts."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "target"
    original_dir.mkdir()
    target_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.write_text(f"original content {i}")
        files.append(test_file)

    # Create conflicting files in target directory
    for i in range(1001, 1004):
        conflict_file = target_dir / f"new_prefix.{i:04d}.exr"
        conflict_file.write_text(f"conflicting content {i}")

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get copy plan
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.copy(new_components, target_dir)

    # Verify conflicts are detected
    assert plan.has_conflicts
    assert len(plan.conflicts) == 3

    # Attempt execute should fail due to conflicts
    with pytest.raises(FileExistsError):
        plan.execute()

    # Original files should still exist and be unchanged
    assert all(f.exists() for f in files)
    for i, f in enumerate(files):
        assert f.read_text() == f"original content {1001 + i}"


def test_file_sequence_copy_partial_conflicts(tmp_path):
    """Test copy behavior with partial conflicts."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "target"
    original_dir.mkdir()
    target_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.write_text(f"original content {i}")
        files.append(test_file)

    # Create conflicting file for only the middle frame
    conflict_file = target_dir / "new_prefix.1002.exr"
    conflict_file.write_text("conflicting content")

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get copy plan
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.copy(new_components, target_dir)

    # Verify partial conflict is detected
    assert plan.has_conflicts
    assert len(plan.conflicts) == 1

    # Original files should be unchanged
    assert all(f.exists() for f in files)


def test_file_sequence_copy_successful_operation(tmp_path):
    """Test successful copy operation."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "target"
    original_dir.mkdir()
    target_dir.mkdir()

    # Create a sequence of files
    files = []
    original_contents = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        content = f"original content {i}"
        test_file.write_text(content)
        files.append(test_file)
        original_contents.append(content)

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get copy plan
    new_components = Components(prefix="copied")
    new_sequence, plan = sequence.copy(new_components, target_dir)

    # No conflicts
    assert not plan.has_conflicts

    # Execute the plan
    plan.execute()

    # New sequence is a separate object
    assert new_sequence is not sequence

    # Check that new files exist with correct content
    for i, content in enumerate(original_contents):
        frame_num = 1001 + i
        new_file = target_dir / f"copied.{frame_num:04d}.exr"
        assert new_file.exists()
        assert new_file.read_text() == content

    # Original files should still exist and be unchanged
    assert all(f.exists() for f in files)
    for i, f in enumerate(files):
        assert f.read_text() == original_contents[i]

    # New sequence should have correct properties
    assert new_sequence.prefix == "copied"
    assert len(new_sequence.items) == len(sequence.items)


def test_file_sequence_copy_same_directory_conflict(tmp_path):
    """Test copy in same directory with name conflict."""
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

    # Copy to same directory with same prefix triggers _copy suffix
    new_components = Components(prefix="test")  # Same prefix
    new_sequence, plan = sequence.copy(new_components, original_dir)

    # Should succeed with _copy suffix (no conflicts)
    assert not plan.has_conflicts

    # Execute
    plan.execute()

    # Check that new files exist with _copy suffix
    for i in range(1001, 1004):
        new_file = original_dir / f"test_copy.{i:04d}.exr"
        assert new_file.exists()
        assert new_file.read_text() == f"content {i}"

    # Original files should still exist
    assert all(f.exists() for f in files)


def test_file_sequence_copy_nonexistent_source_files(tmp_path):
    """Test copy behavior when source files don't exist."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "target"
    original_dir.mkdir()
    target_dir.mkdir()

    # Create sequence items that reference nonexistent files
    items = []
    for i in range(1001, 1004):
        item = Item.from_file_name(f"test.{i:04d}.exr", original_dir)
        items.append(item)

    sequence = FileSequence(tuple(items))

    # Verify files don't exist
    assert all(not item.exists for item in sequence.items)

    # Copy plan should still work (creates new items)
    new_components = Components(prefix="copied")
    new_sequence, plan = sequence.copy(new_components, target_dir)

    # Execute - copying nonexistent files will fail
    result = plan.execute()

    # Should have failures
    assert len(result.failed) > 0


def test_file_sequence_copy_create_directory(tmp_path):
    """Test copy with create_directory=True."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "nonexistent" / "nested" / "target"
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

    # Target directory doesn't exist
    assert not target_dir.exists()

    # Copy with create_directory=True should succeed
    new_components = Components(prefix="copied")
    new_sequence, plan = sequence.copy(new_components, target_dir, create_directory=True)

    # Execute
    plan.execute()

    # Should succeed and create directory
    assert target_dir.exists()

    # Check that new files exist
    for i in range(1001, 1004):
        new_file = target_dir / f"copied.{i:04d}.exr"
        assert new_file.exists()
        assert new_file.read_text() == f"content {i}"


def test_file_sequence_copy_without_create_directory(tmp_path):
    """Test copy without create_directory when target doesn't exist."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "nonexistent"
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

    # Target directory doesn't exist
    assert not target_dir.exists()

    # Copy without create_directory
    new_components = Components(prefix="copied")
    new_sequence, plan = sequence.copy(new_components, target_dir, create_directory=False)

    # Execute should fail (directory doesn't exist)
    result = plan.execute()
    assert len(result.failed) > 0


def test_file_sequence_copy_inspect_plan_without_execute(tmp_path):
    """Test that copy returns plan without executing."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "target"
    original_dir.mkdir()
    target_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.write_text(f"content {i}")
        files.append(test_file)

    # Create conflicting files in target
    for i in range(1001, 1004):
        conflict_file = target_dir / f"copied.{i:04d}.exr"
        conflict_file.write_text("conflict")

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get copy plan (don't execute)
    new_components = Components(prefix="copied")
    new_sequence, plan = sequence.copy(new_components, target_dir)

    # New sequence should reflect proposed state
    assert new_sequence is not sequence
    assert all(item.prefix == "copied" for item in new_sequence.items)

    # Conflicting files should still have original content (not overwritten)
    for i in range(1001, 1004):
        conflict_file = target_dir / f"copied.{i:04d}.exr"
        assert conflict_file.exists()
        assert conflict_file.read_text() == "conflict"  # Unchanged


def test_file_sequence_copy_empty_sequence():
    """Test copy with empty sequence."""
    # Create empty sequence
    sequence = FileSequence(())

    # Should fail validation (empty sequences can't be validated)
    new_components = Components(prefix="copied")
    with pytest.raises(ValueError, match="Empty sequence"):
        sequence.copy(new_components, Path("/tmp"))


def test_file_sequence_copy_type_validation(tmp_path):
    """Test copy parameter type validation."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create single file
    test_file = original_dir / "test.1001.exr"
    test_file.write_text("content")

    # Create sequence
    item = Item.from_path(test_file)
    sequence = FileSequence((item,))

    # Test string new_name (should fail)
    with pytest.raises(TypeError) as exc_info:
        sequence.copy("string_name", original_dir)
    assert "Components object" in str(exc_info.value)

    # Test string new_directory (should fail)
    with pytest.raises(TypeError) as exc_info:
        sequence.copy(Components(prefix="test"), "/tmp/string/path")
    assert "Path object" in str(exc_info.value)
