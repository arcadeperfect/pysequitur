import pytest
from pathlib import Path
from pysequitur import Item


def test_item_move_conflict_detection(parse_item_yaml):
    """Test that move detects conflicts via plan.has_conflicts."""
    test_env_list = parse_item_yaml()

    # Test unlinked items (no real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"])

        assert isinstance(item, Item)
        assert item.exists is False

        new_item, plan = item.move(Path("imaginary_path"))
        # Plan is created but will fail on execute
        result = plan.execute()
        # Should fail because source file doesn't exist
        assert not result.success
        assert len(result.failed) > 0

    # Test linked items (real file associated)
    for test_case in test_env_list:
        move_to_dir = Path(test_case["tmp_dir"] / "move_to")
        move_to_dir.mkdir(parents=True, exist_ok=True)

        data = test_case["data"]
        item = Item.from_file_name(data["file_name"], test_case["real_file"].parent)

        assert isinstance(item, Item)
        assert item.exists

        # Test initial move - no conflict
        new_item, plan = item.move(move_to_dir)
        assert plan.sources[0] == item.absolute_path
        assert plan.destinations[0] == move_to_dir / item.filename
        assert not plan.has_conflicts

        # Create conflicting file
        (move_to_dir / item.filename).touch()

        # Now check for conflicts again
        new_item2, plan2 = item.move(move_to_dir)
        assert plan2.sources[0] == item.absolute_path
        assert plan2.destinations[0] == move_to_dir / item.filename
        assert plan2.has_conflicts

        # Execute should fail due to conflict
        with pytest.raises(FileExistsError):
            plan2.execute()

        (move_to_dir / item.filename).unlink()
