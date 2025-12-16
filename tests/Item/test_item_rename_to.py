import pytest
from pathlib import Path
from pysequitur import Item
from pysequitur.file_sequence import Components


def test_item_rename(parse_item_yaml):
    test_env_list = parse_item_yaml()

    # Test unlinked items (no real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"])

        assert isinstance(item, Item)
        assert item.exists is False

        # Test prefix rename - new API returns (new_item, plan)
        new_item, plan = item.rename(Components(prefix="new_prefix"))
        assert new_item.prefix == "new_prefix"
        # Original item is unchanged (frozen)
        assert item.prefix == data["prefix"]

        # Test delimiter rename
        new_item, plan = item.rename(Components(delimiter="_"))
        assert new_item.delimiter == "_"
        new_item2, plan = new_item.rename(Components(delimiter="-"))
        assert new_item2.delimiter == "-"

        # Test padding rename
        new_padding = 5
        min_padding = len(str(data["frame_number"]))
        new_item, plan = item.rename(Components(padding=new_padding))
        assert new_item.padding == max(new_padding, min_padding)

        # Test suffix and extension rename
        new_item, plan = item.rename(Components(suffix="new_suffix"))
        assert new_item.suffix == "new_suffix"
        new_item, plan = item.rename(Components(extension="new_extension"))
        assert new_item.extension == "new_extension"

    # Test linked items (with real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"], test_case["real_file"].parent)

        assert isinstance(item, Item)
        assert item.exists is True

        # Test prefix rename with execution
        original_path = Path(item.absolute_path)
        new_item, plan = item.rename(Components(prefix="new_prefix"))
        assert new_item.prefix == "new_prefix"
        plan.execute()
        assert not original_path.exists()
        assert new_item.exists is True

        # Continue with the renamed item
        item = new_item

        # Test delimiter rename
        original_path = Path(item.absolute_path)
        new_item, plan = item.rename(Components(delimiter="_"))
        assert new_item.delimiter == "_"
        if plan.operations:
            plan.execute()
        if not data["delimiter"] == "_":
            assert not original_path.exists()
        assert new_item.exists is True

        item = new_item
        original_path = Path(item.absolute_path)
        new_item, plan = item.rename(Components(delimiter="-"))
        assert new_item.delimiter == "-"
        if plan.operations:
            plan.execute()
        assert not original_path.exists()
        assert new_item.exists is True

        item = new_item

        # Test padding rename
        original_path = Path(item.absolute_path)
        new_padding = 5
        min_padding = len(str(data["frame_number"]))
        new_item, plan = item.rename(Components(padding=new_padding))
        expected_padding = max(new_padding, min_padding)
        assert new_item.padding == expected_padding
        if plan.operations:
            plan.execute()
        if expected_padding != item.padding:
            assert not original_path.exists()
        assert new_item.exists is True

        item = new_item

        # Test suffix and extension rename
        original_path = Path(item.absolute_path)
        new_item, plan = item.rename(Components(suffix="new_suffix"))
        assert new_item.suffix == "new_suffix"
        if plan.operations and not plan.has_conflicts:
            plan.execute()
            assert not original_path.exists()
            assert new_item.exists is True
        elif plan.has_conflicts:
            # If there's a conflict (from previous test iteration), skip execution
            pass

        item = new_item
        original_path = Path(item.absolute_path)
        new_item, plan = item.rename(Components(extension="new_extension"))
        assert new_item.extension == "new_extension"
        if plan.operations and not plan.has_conflicts:
            plan.execute()
            assert not original_path.exists()
            assert new_item.exists is True
        elif plan.has_conflicts:
            # If there's a conflict (from previous test iteration), skip execution
            pass
        else:
            # No operations needed (already has this extension)
            pass
