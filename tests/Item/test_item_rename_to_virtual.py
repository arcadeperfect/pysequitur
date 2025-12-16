import pytest
from pathlib import Path
from pysequitur import Item
from pysequitur.file_sequence import Components


def test_item_rename_without_execute(parse_item_yaml):
    """Test that rename returns proposed state without executing."""
    test_env_list = parse_item_yaml()

    # Test linked items (with real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"], test_case["real_file"].parent)

        assert isinstance(item, Item)
        assert item.exists is True
        original_path = Path(item.absolute_path)

        # Test rename without executing - should not change filesystem
        new_item, plan = item.rename(Components(prefix="new_prefix"))
        assert new_item.prefix == "new_prefix"
        assert item.prefix == data["prefix"]  # Original item unchanged (frozen)
        assert original_path.exists()  # Original file still exists

        # Test delimiter rename without execute
        new_item, plan = item.rename(Components(delimiter="-"))
        assert new_item.delimiter == "-"
        assert item.delimiter == data["delimiter"]  # Original item unchanged
        assert original_path.exists()  # Original file still exists

        # Test padding rename without execute
        new_padding = 5
        new_item, plan = item.rename(Components(padding=new_padding))
        assert new_item.padding == max(new_padding, len(str(data["frame_number"])))
        assert item.padding == data["padding"]  # Original item unchanged
        assert original_path.exists()  # Original file still exists

        # Test suffix rename without execute
        new_item, plan = item.rename(Components(suffix="new_suffix"))
        assert new_item.suffix == "new_suffix"
        assert item.suffix == data["suffix"]  # Original item unchanged
        assert original_path.exists()  # Original file still exists

        # Test extension rename without execute
        new_item, plan = item.rename(Components(extension="new_extension"))
        assert new_item.extension == "new_extension"
        assert item.extension == data["extension"]  # Original item unchanged
        assert original_path.exists()  # Original file still exists
