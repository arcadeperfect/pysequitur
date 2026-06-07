import pytest
from pathlib import Path
import shutil
from pysequitur import Item


def test_item_move(parse_item_yaml):
    test_env_list = parse_item_yaml()

    # Test unlinked items (no real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"])

        assert isinstance(item, Item)
        assert item.exists is False

        # Move returns a plan, but executing on non-existent file should fail
        new_item, plan = item.move(Path("imaginary_path"))
        result = plan.execute()
        # Should fail because source file doesn't exist
        assert not result.success
        assert len(result.failed) > 0

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

        new_item, plan = item.move(move_to_dir)
        plan.execute()

        assert new_item.exists
        assert new_item.directory == move_to_dir
        assert not original_path.exists()

        shutil.rmtree(move_to_dir)
