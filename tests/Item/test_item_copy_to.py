import pytest
from pathlib import Path
import shutil
from pysequitur import Item
from pysequitur.file_sequence import Components


def test_item_copy(parse_item_yaml):
    test_env_list = parse_item_yaml()

    # Test unlinked items (no real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"])

        assert isinstance(item, Item)
        assert item.exists is False

        new_item, plan = item.copy()
        assert new_item.prefix == data["prefix"] + "_copy"

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

        # Test copy with new directory
        copied_item_1, plan = item.copy(new_directory=move_to_dir)
        plan.execute()
        assert copied_item_1.exists
        assert copied_item_1.directory == move_to_dir
        assert copied_item_1.prefix == data["prefix"]
        copied_item_1.absolute_path.unlink()

        # Test copy with default settings (adds '_copy' to prefix)
        copied_item_2, plan = item.copy()
        plan.execute()
        assert copied_item_2.exists
        assert copied_item_2.directory == item.directory
        assert copied_item_2.prefix == data["prefix"] + "_copy"
        copied_item_2.absolute_path.unlink()

        # Test copy with new prefix
        copied_item_3, plan = item.copy(Components(prefix="new_prefix"))
        plan.execute()
        assert copied_item_3.exists
        assert copied_item_3.directory == item.directory
        assert copied_item_3.prefix == "new_prefix"
        copied_item_3.absolute_path.unlink()

        shutil.rmtree(move_to_dir)
