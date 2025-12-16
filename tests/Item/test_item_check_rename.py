import pytest
from pathlib import Path
from pysequitur import Item
from pysequitur.file_sequence import Components


def test_item_rename_conflict_detection(parse_item_yaml):
    """Test that rename detects conflicts via plan.has_conflicts."""
    test_env_list = parse_item_yaml()

    # Test unlinked items (no real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"])

        assert isinstance(item, Item)
        assert item.exists is False

        new_item, plan = item.rename(Components(prefix="new_prefix"))
        assert not plan.has_conflicts

    # Test linked items (with real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"], test_case["real_file"].parent)

        assert isinstance(item, Item)
        assert item.exists is True

        new_item, plan = item.rename(Components(prefix="new_prefix"))
        assert plan.sources[0] == item.absolute_path
        assert not plan.has_conflicts

        # Create a file at the target path
        new_path = plan.destinations[0]
        new_path.touch()
        assert new_path.exists()

        # Now check for conflicts again
        new_item2, plan2 = item.rename(Components(prefix="new_prefix"))
        assert plan2.has_conflicts

        new_path.unlink()
