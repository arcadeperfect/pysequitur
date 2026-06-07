import pytest
from pathlib import Path
from pysequitur import Item, FileSequence
from pysequitur.file_sequence import Components


def test_file_sequence_rename_plan_no_conflicts(tmp_path):
    """Test rename plan when no conflicts exist."""
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

    # Test rename plan with new prefix (no conflicts expected)
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.rename(new_components)

    # Should not have conflicts
    assert not plan.has_conflicts
    assert len(plan.operations) == 3

    # Check plan destinations
    for i, op in enumerate(plan.operations):
        expected_new_name = f"new_prefix.{1001 + i:04d}.exr"
        assert op.destination.name == expected_new_name
        assert op.destination.parent == original_dir


def test_file_sequence_rename_plan_with_conflicts(tmp_path):
    """Test rename plan when conflicts exist."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting files with new prefix
    for i in range(1001, 1004):
        conflict_file = original_dir / f"new_prefix.{i:04d}.exr"
        conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test rename plan with conflicting prefix
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.rename(new_components)

    # Should have conflicts
    assert plan.has_conflicts
    assert len(plan.conflicts) == 3


def test_file_sequence_rename_plan_partial_conflicts(tmp_path):
    """Test rename plan when only some files have conflicts."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting file for only the middle frame
    conflict_file = original_dir / "new_prefix.1002.exr"
    conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test rename plan with partial conflicts
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.rename(new_components)

    # Should have partial conflicts
    assert plan.has_conflicts
    assert len(plan.conflicts) == 1  # Only middle file conflicts


def test_file_sequence_rename_plan_change_extension(tmp_path):
    """Test rename plan when changing file extension."""
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

    # Test rename plan to change extension to jpg
    new_components = Components(extension="jpg")
    new_sequence, plan = sequence.rename(new_components)

    # Should have conflicts because .jpg files already exist
    assert plan.has_conflicts
    assert len(plan.conflicts) == 3


def test_file_sequence_rename_plan_change_padding(tmp_path):
    """Test rename plan when changing padding."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence with 4-digit padding
    files = []
    for i in range(101, 104):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting file with 3-digit padding
    conflict_file = original_dir / f"test.{102:03d}.exr"
    conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test rename plan with 3-digit padding
    new_components = Components(padding=3)
    new_sequence, plan = sequence.rename(new_components)

    # Should have partial conflict (102 exists as test.102.exr)
    assert plan.has_conflicts
    assert len(plan.conflicts) == 1


def test_file_sequence_rename_plan_change_delimiter(tmp_path):
    """Test rename plan when changing delimiter."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence with underscore delimiter
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test_{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting files with dot delimiter
    for i in range(1001, 1004):
        conflict_file = original_dir / f"test.{i:04d}.exr"
        conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test rename plan to change delimiter from _ to .
    new_components = Components(delimiter=".")
    new_sequence, plan = sequence.rename(new_components)

    # Should have conflicts
    assert plan.has_conflicts
    assert len(plan.conflicts) == 3


def test_file_sequence_rename_plan_change_suffix(tmp_path):
    """Test rename plan when changing suffix."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence without suffix
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting files with suffix
    for i in range(1001, 1004):
        conflict_file = original_dir / f"test.{i:04d}_final.exr"
        conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test rename plan to add suffix
    new_components = Components(suffix="_final")
    new_sequence, plan = sequence.rename(new_components)

    # Should have conflicts
    assert plan.has_conflicts
    assert len(plan.conflicts) == 3


def test_file_sequence_rename_plan_multiple_changes(tmp_path):
    """Test rename plan when changing multiple components."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test rename plan with multiple changes (no conflicts expected)
    new_components = Components(
        prefix="render", delimiter="_", padding=5, suffix="_final", extension="png"
    )
    new_sequence, plan = sequence.rename(new_components)

    # Should not have conflicts
    assert not plan.has_conflicts
    assert len(plan.operations) == 3

    # Check destinations
    for i, op in enumerate(plan.operations):
        frame_num = 1001 + i
        expected_name = f"render_{frame_num:05d}_final.png"
        assert op.destination.name == expected_name


def test_file_sequence_rename_plan_empty_sequence():
    """Test rename plan with empty sequence."""
    # Create empty sequence
    sequence = FileSequence(())

    # Test rename plan
    new_components = Components(prefix="new_name")
    new_sequence, plan = sequence.rename(new_components)

    # Should return empty plan
    assert len(plan.operations) == 0
    assert not plan.has_conflicts


def test_file_sequence_rename_plan_same_name(tmp_path):
    """Test rename plan when renaming to the same name."""
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

    # Test rename plan to same name - should be empty plan
    new_components = Components(prefix="test")  # Same as current
    new_sequence, plan = sequence.rename(new_components)

    # Should be empty plan (no changes needed)
    assert len(plan.operations) == 0
    assert not plan.has_conflicts


def test_file_sequence_rename_plan_execute_success(tmp_path):
    """Test executing a successful rename plan."""
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

    # Get plan and verify no conflicts
    new_components = Components(prefix="new_name")
    new_sequence, plan = sequence.rename(new_components)
    assert not plan.has_conflicts

    # Execute the plan
    plan.execute()

    # Original files should be gone
    assert all(not f.exists() for f in files)

    # New files should exist
    for i in range(1001, 1004):
        new_file = original_dir / f"new_name.{i:04d}.exr"
        assert new_file.exists()

    # New sequence should reflect the changes
    assert all(item.prefix == "new_name" for item in new_sequence.items)


def test_file_sequence_rename_plan_execute_with_conflicts(tmp_path):
    """Test executing rename plan with conflicts raises error."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting file
    conflict_file = original_dir / "new_prefix.1002.exr"
    conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get plan and verify it has conflicts
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.rename(new_components)
    assert plan.has_conflicts

    # Executing should fail
    with pytest.raises(FileExistsError):
        plan.execute()

    # Original files should still exist
    assert all(f.exists() for f in files)


def test_file_sequence_rename_plan_with_none_components(tmp_path):
    """Test rename plan behavior with None values in Components."""
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

    # Test rename plan with Components that only changes one thing
    new_components = Components(prefix="new_prefix")  # Only prefix, others None
    new_sequence, plan = sequence.rename(new_components)

    # Should not have conflicts
    assert not plan.has_conflicts
    assert len(plan.operations) == 3

    # Check destinations keep other components the same
    for i, op in enumerate(plan.operations):
        frame_num = 1001 + i
        expected_name = f"new_prefix.{frame_num:04d}.exr"
        assert op.destination.name == expected_name
