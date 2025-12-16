import pytest
from pathlib import Path
import shutil
from pysequitur import Item


def test_item_move_without_execute(parse_item_yaml):
    """Test that move returns proposed state without executing."""
    test_env_list = parse_item_yaml()

    # Test linked items (with real file associated)
    for test_case in test_env_list:
        move_to_dir = Path(test_case["tmp_dir"] / "move_to")
        move_to_dir.mkdir(parents=True, exist_ok=True)

        data = test_case["data"]
        item = Item.from_file_name(data["file_name"], test_case["real_file"].parent)

        assert isinstance(item, Item)
        original_path = Path(item.absolute_path)
        assert original_path.exists()
        assert item.exists

        # Move without executing - should not change filesystem
        new_item, plan = item.move(move_to_dir)

        # New item has the proposed new state
        assert new_item.directory == move_to_dir

        # Original item is unchanged (frozen)
        assert item.directory == test_case["real_file"].parent

        # Original file still exists
        assert original_path.exists()

        # New path doesn't exist yet
        assert not new_item.exists

        shutil.rmtree(move_to_dir)
