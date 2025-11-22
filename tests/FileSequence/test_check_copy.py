from pysequitur import FileSequence, Item
from pysequitur.file_sequence import Components


def test_file_sequence_check_copy_no_conflicts(tmp_path):
    """Test check_copy when no conflicts exist."""
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

    # Test check_copy with new prefix (no conflicts expected)
    new_components = Components(prefix="new_prefix")
    check_results = sequence.check_copy(new_name=new_components)

    # Should return list of tuples for each item
    assert len(check_results) == 3

    for i, (original_path, new_path, conflict_exists) in enumerate(check_results):
        # Check original path matches
        assert original_path == sequence.items[i].absolute_path

        # Check new path is constructed correctly
        expected_new_name = f"new_prefix.{1001 + i:04d}.exr"
        assert new_path.name == expected_new_name
        assert new_path.parent == original_dir

        # No conflicts should exist
        assert conflict_exists is False


def test_file_sequence_check_copy_with_conflicts(tmp_path):
    """Test check_copy when conflicts exist."""
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

    # Create conflicting files with new prefix
    conflicting_files = []
    for i in range(1001, 1004):
        conflict_file = original_dir / f"new_prefix.{i:04d}.exr"
        conflict_file.touch()
        conflicting_files.append(conflict_file)

    # Test check_copy with new prefix (conflicts expected)
    new_components = Components(prefix="new_prefix")
    check_results = sequence.check_copy(new_name=new_components)

    # Should return list of tuples for each item
    assert len(check_results) == 3

    for i, (original_path, new_path, conflict_exists) in enumerate(check_results):
        # Check original path matches
        assert original_path == sequence.items[i].absolute_path

        # Check new path is constructed correctly
        expected_new_name = f"new_prefix.{1001 + i:04d}.exr"
        assert new_path.name == expected_new_name

        # Conflicts should exist
        assert conflict_exists is True


def test_file_sequence_check_copy_new_directory(tmp_path):
    """Test check_copy with new directory."""
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test check_copy to new directory
    check_results = sequence.check_copy(new_directory=new_dir)

    # Should return list of tuples for each item
    assert len(check_results) == 3

    for i, (original_path, new_path, conflict_exists) in enumerate(check_results):
        # Check original path matches
        assert original_path == sequence.items[i].absolute_path

        # Check new path is in new directory
        expected_new_name = f"test.{1001 + i:04d}.exr"
        assert new_path.name == expected_new_name
        assert new_path.parent == new_dir

        # No conflicts should exist
        assert conflict_exists is False


def test_file_sequence_check_copy_new_directory_with_conflicts(tmp_path):
    """Test check_copy with new directory where conflicts exist."""
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test check_copy to new directory with conflicts
    check_results = sequence.check_copy(new_directory=new_dir)

    # Should return list of tuples for each item
    assert len(check_results) == 3

    for i, (original_path, new_path, conflict_exists) in enumerate(check_results):
        # Check original path matches
        assert original_path == sequence.items[i].absolute_path

        # Check new path is in new directory
        expected_new_name = f"test.{1001 + i:04d}.exr"
        assert new_path.name == expected_new_name
        assert new_path.parent == new_dir

        # Conflicts should exist
        assert conflict_exists is True


def test_file_sequence_check_copy_both_name_and_directory(tmp_path):
    """Test check_copy with both new name and new directory."""
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
    items = [Item.from_path(f) for f in files]
    sequence = FileSequence([item for item in items if item is not None])

    # Test check_copy with both new name and directory
    new_components = Components(prefix="new_prefix", extension="png")
    check_results = sequence.check_copy(new_name=new_components, new_directory=new_dir)

    # Should return list of tuples for each item
    assert len(check_results) == 3

    for i, (original_path, new_path, conflict_exists) in enumerate(check_results):
        # Check original path matches
        assert original_path == sequence.items[i].absolute_path

        # Check new path has new name and directory
        expected_new_name = f"new_prefix.{1001 + i:04d}.png"
        assert new_path.name == expected_new_name
        assert new_path.parent == new_dir

        # No conflicts should exist
        assert conflict_exists is False


def test_file_sequence_check_copy_defaults(tmp_path):
    """Test check_copy with default parameters (None for both)."""
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

    # Test check_copy with defaults
    # When no parameters provided, it uses same name/directory initially,
    # but detects path collision and adds "_copy" to prefix
    check_results = sequence.check_copy()

    # Should return list of tuples for each item
    assert len(check_results) == 3

    for i, (original_path, new_path, conflict_exists) in enumerate(check_results):
        # Check original path matches
        assert original_path == sequence.items[i].absolute_path

        # Should add "_copy" to prefix when paths would be identical
        expected_new_name = f"test_copy.{1001 + i:04d}.exr"
        assert new_path.name == expected_new_name
        assert new_path.parent == original_dir

        # No conflicts should exist with the "_copy" suffix
        assert conflict_exists is False


def test_file_sequence_check_copy_empty_sequence():
    """Test check_copy with empty sequence."""
    # Create empty sequence
    sequence = FileSequence([])

    # Test check_copy
    check_results = sequence.check_copy()

    # Should return empty list
    assert check_results == []


def test_file_sequence_check_copy_partial_conflicts(tmp_path):
    """Test check_copy where only some files have conflicts."""
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

    # Create conflicting file for only the middle frame
    conflict_file = original_dir / "new_prefix.1002.exr"
    conflict_file.touch()

    # Test check_copy with new prefix
    new_components = Components(prefix="new_prefix")
    check_results = sequence.check_copy(new_name=new_components)

    # Should return list of tuples for each item
    assert len(check_results) == 3

    # Check each result
    expected_conflicts = [False, True, False]  # Only middle file conflicts

    for i, (original_path, _new_path, conflict_exists) in enumerate(check_results):
        assert original_path == sequence.items[i].absolute_path
        assert conflict_exists == expected_conflicts[i]
