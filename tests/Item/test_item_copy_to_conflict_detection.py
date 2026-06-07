import pytest
from pathlib import Path
from pysequitur import Item
from pysequitur.file_sequence import Components


def test_item_copy_conflict_detection_detailed(tmp_path):
    """Test that Item.copy properly detects and prevents conflicts."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "target"
    original_dir.mkdir()
    target_dir.mkdir()

    # Create original file
    original_file = original_dir / "test.1001.exr"
    original_file.write_text("original content")

    # Create conflicting file in target
    conflict_file = target_dir / "new_name.1001.exr"
    conflict_file.write_text("conflicting content")

    # Create item
    item = Item.from_path(original_file)

    # Copy should detect conflict
    new_components = Components(prefix="new_name")
    new_item, plan = item.copy(new_components, target_dir)
    
    # Plan should have conflicts
    assert plan.has_conflicts
    
    # Attempting to execute should fail
    with pytest.raises(FileExistsError):
        plan.execute()

    # Original file should be unchanged
    assert original_file.exists()
    assert original_file.read_text() == "original content"

    # Conflicting file should be unchanged
    assert conflict_file.exists()
    assert conflict_file.read_text() == "conflicting content"


def test_item_copy_successful_operation(tmp_path):
    """Test successful Item.copy operation."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "target"
    original_dir.mkdir()
    target_dir.mkdir()

    # Create original file
    original_file = original_dir / "test.1001.exr"
    original_content = "original content"
    original_file.write_text(original_content)

    # Create item
    item = Item.from_path(original_file)

    # Perform copy
    new_components = Components(prefix="copied")
    new_item, plan = item.copy(new_components, target_dir)

    # No conflicts
    assert not plan.has_conflicts

    # Execute the plan
    plan.execute()

    # Should return new Item object
    assert new_item is not item
    assert isinstance(new_item, Item)

    # Check that new file exists with correct content
    new_file = target_dir / "copied.1001.exr"
    assert new_file.exists()
    assert new_file.read_text() == original_content

    # Original file should still exist and be unchanged
    assert original_file.exists()
    assert original_file.read_text() == original_content

    # New item should have correct properties
    assert new_item.prefix == "copied"
    assert new_item.frame_number == 1001
    assert new_item.extension == "exr"
    assert new_item.exists


def test_item_copy_same_path_adds_copy_suffix(tmp_path):
    """Test that copying to same path adds _copy suffix."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create original file
    original_file = original_dir / "test.1001.exr"
    original_file.write_text("original content")

    # Create item
    item = Item.from_path(original_file)

    # Copy to same name in same directory
    new_components = Components(prefix="test")  # Same prefix
    new_item, plan = item.copy(new_components, original_dir)

    # Execute
    plan.execute()

    # Should succeed with _copy suffix
    assert new_item is not item

    # Check that new file exists with _copy suffix
    new_file = original_dir / "test_copy.1001.exr"
    assert new_file.exists()
    assert new_file.read_text() == "original content"

    # Original file should still exist
    assert original_file.exists()

    # New item should have _copy prefix
    assert new_item.prefix == "test_copy"


def test_item_copy_nonexistent_source_file(tmp_path):
    """Test copy behavior when source file doesn't exist."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "target"
    original_dir.mkdir()
    target_dir.mkdir()

    # Create item without creating the actual file
    item = Item.from_file_name("test.1001.exr", original_dir)

    # Verify file doesn't exist
    assert not item.exists

    # Copy should still create a plan
    new_components = Components(prefix="copied")
    new_item, plan = item.copy(new_components, target_dir)

    # Should return new item
    assert new_item is not item
    assert isinstance(new_item, Item)

    # Executing should fail since source doesn't exist
    result = plan.execute()
    # The execution fails but doesn't raise (failed is captured in result)
    assert len(result.failed) > 0 or not new_item.exists


def test_item_copy_without_execute(tmp_path):
    """Test copy without executing (preview mode)."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "target"
    original_dir.mkdir()
    target_dir.mkdir()

    # Create original file
    original_file = original_dir / "test.1001.exr"
    original_file.write_text("original content")

    # Create conflicting file in target
    conflict_file = target_dir / "copied.1001.exr"
    conflict_file.write_text("conflicting content")

    # Create item
    item = Item.from_path(original_file)

    # Get copy plan without executing
    new_components = Components(prefix="copied")
    new_item, plan = item.copy(new_components, target_dir)

    # Should return new item
    assert new_item is not item
    assert isinstance(new_item, Item)

    # Should detect conflict
    assert plan.has_conflicts

    # Conflicting file should still exist with original content
    assert conflict_file.exists()
    assert conflict_file.read_text() == "conflicting content"


def test_item_copy_type_validation(tmp_path):
    """Test copy parameter type validation."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create original file
    original_file = original_dir / "test.1001.exr"
    original_file.write_text("content")

    # Create item
    item = Item.from_path(original_file)

    # Test string new_name (should fail)
    with pytest.raises(TypeError) as exc_info:
        item.copy("string_name", original_dir)
    assert "Components object" in str(exc_info.value)


def test_item_copy_none_new_name(tmp_path):
    """Test copy with None new_name (should use default)."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "target"
    original_dir.mkdir()
    target_dir.mkdir()

    # Create original file
    original_file = original_dir / "test.1001.exr"
    original_file.write_text("content")

    # Create item
    item = Item.from_path(original_file)

    # Copy with None new_name
    new_item, plan = item.copy(None, target_dir)
    plan.execute()

    # Should succeed with same name
    assert new_item is not item

    # Check that new file exists with same name
    new_file = target_dir / "test.1001.exr"
    assert new_file.exists()
    assert new_file.read_text() == "content"


def test_item_copy_none_new_directory(tmp_path):
    """Test copy with None new_directory (should use same directory)."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()

    # Create original file
    original_file = original_dir / "test.1001.exr"
    original_file.write_text("content")

    # Create item
    item = Item.from_path(original_file)

    # Copy with None new_directory (same name would conflict, so should add _copy)
    new_components = Components(prefix="test")
    new_item, plan = item.copy(new_components, None)
    plan.execute()

    # Should succeed with _copy suffix
    assert new_item is not item

    # Check that new file exists with _copy suffix in same directory
    new_file = original_dir / "test_copy.1001.exr"
    assert new_file.exists()
    assert new_file.read_text() == "content"


def test_item_copy_different_components(tmp_path):
    """Test copy with different component changes."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "target"
    original_dir.mkdir()
    target_dir.mkdir()

    # Create original file
    original_file = original_dir / "test.1001.exr"
    original_file.write_text("content")

    # Create item
    item = Item.from_path(original_file)

    # Test changing multiple components
    new_components = Components(
        prefix="new_name",
        delimiter="_",
        padding=5,
        suffix="_final",
        extension="png",
    )
    new_item, plan = item.copy(new_components, target_dir)
    plan.execute()

    # Should succeed
    assert new_item is not item

    # Check that new file has all changes
    new_file = target_dir / "new_name_01001_final.png"
    assert new_file.exists()
    assert new_file.read_text() == "content"

    # New item should have updated properties
    assert new_item.prefix == "new_name"
    assert new_item.delimiter == "_"
    assert new_item.padding == 5
    assert new_item.suffix == "_final"
    assert new_item.extension == "png"


def test_item_copy_preserves_file_metadata(tmp_path):
    """Test that copy preserves file metadata (using shutil.copy2)."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "target"
    original_dir.mkdir()
    target_dir.mkdir()

    # Create original file
    original_file = original_dir / "test.1001.exr"
    original_file.write_text("content")

    # Get original modification time
    original_mtime = original_file.stat().st_mtime

    # Create item
    item = Item.from_path(original_file)

    # Copy to new location
    new_components = Components(prefix="copied")
    new_item, plan = item.copy(new_components, target_dir)
    plan.execute()

    # Check that new file exists
    new_file = target_dir / "copied.1001.exr"
    assert new_file.exists()

    # Metadata should be preserved (shutil.copy2 preserves timestamps)
    new_mtime = new_file.stat().st_mtime
    assert abs(new_mtime - original_mtime) < 1  # Allow small difference


def test_item_copy_force_overwrite(tmp_path):
    """Test that copy can force overwrite with force=True."""
    # Setup
    original_dir = tmp_path / "original"
    target_dir = tmp_path / "target"
    original_dir.mkdir()
    target_dir.mkdir()

    # Create original file
    original_file = original_dir / "test.1001.exr"
    original_file.write_text("original content")

    # Create conflicting file
    conflict_file = target_dir / "copied.1001.exr"
    conflict_file.write_text("conflict")

    # Create item
    item = Item.from_path(original_file)

    # Get copy plan
    new_components = Components(prefix="copied")
    new_item, plan = item.copy(new_components, target_dir)

    # Should have conflict
    assert plan.has_conflicts

    # Execute with force=True
    result = plan.execute(force=True)

    # Should succeed
    assert result.success

    # File should be overwritten
    assert conflict_file.read_text() == "original content"
