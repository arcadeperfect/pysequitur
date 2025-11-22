import pytest
from pathlib import Path
from pysequitur import Item, FileSequence


def test_file_sequence_check_move_no_conflicts(tmp_path):
    """Test check_move when no conflicts exist."""
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

    # Test check_move to empty directory (no conflicts expected)
    check_results = sequence.check_move(target_dir)

    # Should return list of tuples for each item
    assert len(check_results) == 3
    
    for i, (original_path, new_path, conflict_exists) in enumerate(check_results):
        # Check original path matches
        assert original_path == sequence.items[i].absolute_path
        
        # Check new path is constructed correctly
        expected_new_name = f"test.{1001 + i:04d}.exr"
        assert new_path.name == expected_new_name
        assert new_path.parent == target_dir
        
        # No conflicts should exist
        assert conflict_exists is False


def test_file_sequence_check_move_with_conflicts(tmp_path):
    """Test check_move when conflicts exist."""
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

    # Test check_move with conflicts
    check_results = sequence.check_move(target_dir)

    # Should return list of tuples for each item
    assert len(check_results) == 3
    
    for i, (original_path, new_path, conflict_exists) in enumerate(check_results):
        # Check original path matches
        assert original_path == sequence.items[i].absolute_path
        
        # Check new path is constructed correctly
        expected_new_name = f"test.{1001 + i:04d}.exr"
        assert new_path.name == expected_new_name
        assert new_path.parent == target_dir
        
        # All should have conflicts
        assert conflict_exists is True


def test_file_sequence_check_move_partial_conflicts(tmp_path):
    """Test check_move when only some files have conflicts."""
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test check_move with partial conflicts
    check_results = sequence.check_move(target_dir)

    # Should return list of tuples for each item
    assert len(check_results) == 3
    
    # Check each result - only middle file should have conflict
    expected_conflicts = [False, True, False]
    
    for i, (original_path, new_path, conflict_exists) in enumerate(check_results):
        assert original_path == sequence.items[i].absolute_path
        assert new_path.parent == target_dir
        assert conflict_exists == expected_conflicts[i]


def test_file_sequence_check_move_nonexistent_target_directory(tmp_path):
    """Test check_move with non-existent target directory."""
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test check_move to non-existent directory
    check_results = sequence.check_move(target_dir)

    # Should return list of tuples for each item
    assert len(check_results) == 3
    
    for i, (original_path, new_path, conflict_exists) in enumerate(check_results):
        # Check paths are constructed correctly
        assert original_path == sequence.items[i].absolute_path
        assert new_path.parent == target_dir
        
        # No conflicts since directory doesn't exist (files can't exist there)
        assert conflict_exists is False


def test_file_sequence_check_move_same_directory(tmp_path):
    """Test check_move when moving to the same directory."""
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

    # Test check_move to same directory
    check_results = sequence.check_move(original_dir)

    # Should return list of tuples for each item
    assert len(check_results) == 3
    
    for i, (original_path, new_path, conflict_exists) in enumerate(check_results):
        # Paths should be identical
        assert original_path == new_path
        assert original_path == sequence.items[i].absolute_path
        
        # Should detect conflict with itself
        assert conflict_exists is True


def test_file_sequence_check_move_different_file_types(tmp_path):
    """Test check_move with different file extensions in target."""
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

    # Test check_move - should have no conflicts due to different extensions
    check_results = sequence.check_move(target_dir)

    # Should return list of tuples for each item
    assert len(check_results) == 3
    
    for i, (original_path, new_path, conflict_exists) in enumerate(check_results):
        assert original_path == sequence.items[i].absolute_path
        assert new_path.parent == target_dir
        assert new_path.suffix == ".exr"
        
        # No conflicts due to different extensions
        assert conflict_exists is False


def test_file_sequence_check_move_different_prefixes(tmp_path):
    """Test check_move with different prefixes in target."""
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

    # Test check_move - should have no conflicts due to different prefixes
    check_results = sequence.check_move(target_dir)

    # Should return list of tuples for each item
    assert len(check_results) == 3
    
    for i, (original_path, new_path, conflict_exists) in enumerate(check_results):
        assert original_path == sequence.items[i].absolute_path
        assert new_path.parent == target_dir
        assert "test." in new_path.name
        
        # No conflicts due to different prefixes
        assert conflict_exists is False


def test_file_sequence_check_move_empty_sequence():
    """Test check_move with empty sequence."""
    # Create empty sequence
    sequence = FileSequence([])

    # Test check_move
    target_dir = Path("/some/directory")
    check_results = sequence.check_move(target_dir)

    # Should return empty list
    assert check_results == []


def test_file_sequence_check_move_nested_directories(tmp_path):
    """Test check_move with nested target directories."""
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test check_move
    check_results = sequence.check_move(target_dir)

    # Should return list of tuples for each item
    assert len(check_results) == 2
    
    # First file: no conflict, second file: conflict
    expected_conflicts = [False, True]
    
    for i, (original_path, new_path, conflict_exists) in enumerate(check_results):
        assert original_path == sequence.items[i].absolute_path
        assert new_path.parent == target_dir
        assert conflict_exists == expected_conflicts[i]


def test_file_sequence_check_move_integration_with_move_to(tmp_path):
    """Test that check_move results align with actual move_to behavior."""
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test check_move first
    check_results = sequence.check_move(target_dir)
    
    # Should detect the conflict
    conflicts = [result[2] for result in check_results]
    assert any(conflicts)  # At least one conflict should be detected
    
    # Actual move should fail due to conflicts
    with pytest.raises(FileExistsError):
        sequence.move_to(target_dir)
    
    # Files should still be in original location after failed move
    assert all(f.exists() for f in files)
    assert all(item.directory == original_dir for item in sequence.items)


def test_file_sequence_check_move_return_format_validation(tmp_path):
    """Test that check_move returns the correct format."""
    # Setup
    original_dir = tmp_path / "original"
    original_dir.mkdir()
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # Create a single file for simple validation
    test_file = original_dir / "test.1001.exr"
    test_file.touch()

    # Create sequence
    item = Item.from_path(test_file)
    sequence = FileSequence([item])

    # Test check_move
    check_results = sequence.check_move(target_dir)

    # Validate return format
    assert isinstance(check_results, list)
    assert len(check_results) == 1
    
    result = check_results[0]
    assert isinstance(result, tuple)
    assert len(result) == 3
    
    original_path, new_path, conflict_exists = result
    assert isinstance(original_path, Path)
    assert isinstance(new_path, Path)
    assert isinstance(conflict_exists, bool)
    
    # Validate content
    assert original_path == test_file
    assert new_path == target_dir / "test.1001.exr"
    assert conflict_exists is False
