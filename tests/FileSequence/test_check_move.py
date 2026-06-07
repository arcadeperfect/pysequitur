import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_file_sequence_move_plan_no_conflicts(tmp_path):
    """Test move plan when no conflicts exist."""
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

    # Test move plan to empty directory (no conflicts expected)
    new_sequence, plan = sequence.move(target_dir)

    # Should not have conflicts
    assert not plan.has_conflicts
    assert len(plan.operations) == 3

    # Check plan destinations
    for i, op in enumerate(plan.operations):
        expected_new_name = f"test.{1001 + i:04d}.exr"
        assert op.destination.name == expected_new_name
        assert op.destination.parent == target_dir


def test_file_sequence_move_plan_with_conflicts(tmp_path):
    """Test move plan when conflicts exist."""
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
    for i in range(1001, 1004):
        conflict_file = target_dir / f"test.{i:04d}.exr"
        conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test move plan with conflicts
    new_sequence, plan = sequence.move(target_dir)

    # Should have conflicts
    assert plan.has_conflicts
    assert len(plan.conflicts) == 3


def test_file_sequence_move_plan_partial_conflicts(tmp_path):
    """Test move plan when only some files have conflicts."""
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

    # Create conflicting file for only the middle frame
    conflict_file = target_dir / "test.1002.exr"
    conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test move plan with partial conflicts
    new_sequence, plan = sequence.move(target_dir)

    # Should have partial conflicts
    assert plan.has_conflicts
    assert len(plan.conflicts) == 1  # Only middle file conflicts


def test_file_sequence_move_plan_nonexistent_target_directory(tmp_path):
    """Test move plan with non-existent target directory."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    target_dir = tmp_path / "nonexistent"  # Don't create this directory

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test move plan to non-existent directory
    new_sequence, plan = sequence.move(target_dir)

    # Should not have conflicts (files can't exist in non-existent directory)
    assert not plan.has_conflicts
    assert len(plan.operations) == 3


def test_file_sequence_move_plan_same_directory(tmp_path):
    """Test move plan when moving to the same directory."""
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

    # Test move plan to same directory - should be no-op
    new_sequence, plan = sequence.move(original_dir)

    # Should be an empty plan (no operations needed)
    assert len(plan.operations) == 0
    assert not plan.has_conflicts


def test_file_sequence_move_plan_different_file_types(tmp_path):
    """Test move plan with different file extensions in target."""
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

    # Test move plan - should have no conflicts due to different extensions
    new_sequence, plan = sequence.move(target_dir)

    # Should not have conflicts
    assert not plan.has_conflicts


def test_file_sequence_move_plan_different_prefixes(tmp_path):
    """Test move plan with different prefixes in target."""
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

    # Test move plan - should have no conflicts due to different prefixes
    new_sequence, plan = sequence.move(target_dir)

    # Should not have conflicts
    assert not plan.has_conflicts


def test_file_sequence_move_plan_empty_sequence():
    """Test move plan with empty sequence."""
    # Create empty sequence
    sequence = FileSequence(())

    # Empty sequence has no directory, so moving raises ValueError
    # when trying to check if target == current directory
    target_dir = Path("/some/directory")
    with pytest.raises(ValueError, match="Empty sequence"):
        sequence.move(target_dir)


def test_file_sequence_move_plan_nested_directories(tmp_path):
    """Test move plan with nested target directories."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    target_dir = tmp_path / "nested" / "deep" / "path"
    target_dir.mkdir(parents=True)

    # Create a sequence of files
    files = []
    for i in range(1001, 1003):  # Just 2 files for simpler testing
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create one conflicting file in nested target
    conflict_file = target_dir / "test.1002.exr"
    conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test move plan
    new_sequence, plan = sequence.move(target_dir)

    # Should have partial conflicts
    assert plan.has_conflicts
    assert len(plan.conflicts) == 1  # Only second file conflicts


def test_file_sequence_move_plan_execute_with_conflicts(tmp_path):
    """Test that executing move plan with conflicts raises error."""
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

    # Create one conflicting file
    conflict_file = target_dir / "test.1002.exr"
    conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Get plan and verify it has conflicts
    new_sequence, plan = sequence.move(target_dir)
    assert plan.has_conflicts

    # Executing should fail
    with pytest.raises(FileExistsError):
        plan.execute()

    # Files should still be in original location
    assert all(f.exists() for f in files)
