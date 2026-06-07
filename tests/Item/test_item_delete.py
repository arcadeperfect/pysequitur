import pytest
from pathlib import Path
from pysequitur import Item


def test_item_delete(parse_item_yaml):
    test_env_list = parse_item_yaml()

    # Test unlinked items (no real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"])

        assert isinstance(item, Item)
        assert item.exists is False

        plan = item.delete()
        result = plan.execute()
        # Should fail because file doesn't exist
        assert not result.success
        assert len(result.failed) > 0

    # Test linked items (with real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"], test_case["real_file"].parent)

        assert isinstance(item, Item)
        assert item.exists

        plan = item.delete()
        plan.execute()
        assert not item.exists  # File is gone
