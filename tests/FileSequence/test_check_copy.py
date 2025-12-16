import pytest
from pathlib import Path
from pysequitur import FileSequence, Item
from pysequitur.file_sequence import Components


def test_file_sequence_copy_plan_no_conflicts(tmp_path):
    """Test copy plan when no conflicts exist."""
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

    # Test copy plan with new prefix (no conflicts expected)
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.copy(new_name=new_components)

    # Should not have conflicts
    assert not plan.has_conflicts
    assert len(plan.operations) == 3

    # Check plan destinations
    for i, op in enumerate(plan.operations):
        expected_new_name = f"new_prefix.{1001 + i:04d}.exr"
        assert op.destination.name == expected_new_name
        assert op.destination.parent == original_dir


def test_file_sequence_copy_plan_with_conflicts(tmp_path):
    """Test copy plan when conflicts exist."""
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

    # Create conflicting files with new prefix
    for i in range(1001, 1004):
        conflict_file = original_dir / f"new_prefix.{i:04d}.exr"
        conflict_file.touch()

    # Test copy plan with new prefix (conflicts expected)
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.copy(new_name=new_components)

    # Should have conflicts
    assert plan.has_conflicts
    assert len(plan.conflicts) == 3


def test_file_sequence_copy_plan_new_directory(tmp_path):
    """Test copy plan with new directory."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    new_dir = tmp_path / "new"
    new_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test copy plan to new directory
    new_sequence, plan = sequence.copy(new_directory=new_dir)

    # Should not have conflicts
    assert not plan.has_conflicts
    assert len(plan.operations) == 3

    # Check plan destinations are in new directory
    for i, op in enumerate(plan.operations):
        expected_new_name = f"test.{1001 + i:04d}.exr"
        assert op.destination.name == expected_new_name
        assert op.destination.parent == new_dir


def test_file_sequence_copy_plan_new_directory_with_conflicts(tmp_path):
    """Test copy plan with new directory where conflicts exist."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    new_dir = tmp_path / "new"
    new_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create conflicting files in new directory
    for i in range(1001, 1004):
        conflict_file = new_dir / f"test.{i:04d}.exr"
        conflict_file.touch()

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test copy plan to new directory with conflicts
    new_sequence, plan = sequence.copy(new_directory=new_dir)

    # Should have conflicts
    assert plan.has_conflicts
    assert len(plan.conflicts) == 3


def test_file_sequence_copy_plan_both_name_and_directory(tmp_path):
    """Test copy plan with both new name and new directory."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    new_dir = tmp_path / "new"
    new_dir.mkdir()

    # Create a sequence of files
    files = []
    for i in range(1001, 1004):
        test_file = original_dir / f"test.{i:04d}.exr"
        test_file.touch()
        files.append(test_file)

    # Create sequence
    items = tuple(Item.from_path(f) for f in files if Item.from_path(f) is not None)
    sequence = FileSequence(items)

    # Test copy plan with both new name and directory
    new_components = Components(prefix="new_prefix", extension="png")
    new_sequence, plan = sequence.copy(new_name=new_components, new_directory=new_dir)

    # Should not have conflicts
    assert not plan.has_conflicts
    assert len(plan.operations) == 3

    # Check plan destinations have new name and directory
    for i, op in enumerate(plan.operations):
        expected_new_name = f"new_prefix.{1001 + i:04d}.png"
        assert op.destination.name == expected_new_name
        assert op.destination.parent == new_dir


def test_file_sequence_copy_plan_defaults(tmp_path):
    """Test copy plan with default parameters (None for both)."""
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

    # Test copy plan with defaults
    # When no parameters provided, it adds "_copy" to prefix
    new_sequence, plan = sequence.copy()

    # Should not have conflicts (with "_copy" suffix)
    assert not plan.has_conflicts
    assert len(plan.operations) == 3

    # Check that new items have "_copy" suffix
    assert all(item.prefix == "test_copy" for item in new_sequence.items)


def test_file_sequence_copy_plan_empty_sequence():
    """Test copy plan with empty sequence."""
    # Create empty sequence
    sequence = FileSequence(())

    # Test copy plan - should fail validation
    with pytest.raises(ValueError, match="Empty sequence"):
        sequence.copy()


def test_file_sequence_copy_plan_partial_conflicts(tmp_path):
    """Test copy plan where only some files have conflicts."""
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

    # Create conflicting file for only the middle frame
    conflict_file = original_dir / "new_prefix.1002.exr"
    conflict_file.touch()

    # Test copy plan with new prefix
    new_components = Components(prefix="new_prefix")
    new_sequence, plan = sequence.copy(new_name=new_components)

    # Should have conflicts (partial)
    assert plan.has_conflicts
    assert len(plan.conflicts) == 1  # Only middle file conflicts
