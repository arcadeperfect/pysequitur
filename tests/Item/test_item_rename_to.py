import pytest
from pathlib import Path
from pysequitur import Item
from pysequitur.file_sequence import Components


def test_item_rename_to(parse_item_yaml):
    test_env_list = parse_item_yaml()

    # Test unlinked items (no real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"])

        assert isinstance(item, Item)
        assert item.exists is False

        # Test prefix rename
        item.rename_to(Components(prefix="new_prefix"))
        assert item.prefix == "new_prefix"

        # Test delimiter rename
        item.rename_to(Components(delimiter="_"))
        assert item.delimiter == "_"
        item.rename_to(Components(delimiter="-"))
        assert item.delimiter == "-"

        # Test padding rename
        new_padding = 5
        min_padding = len(str(data["frame_number"]))
        item.rename_to(Components(padding=new_padding))
        assert item.padding == max(new_padding, min_padding)

        # Test suffix and extension rename
        item.rename_to(Components(suffix="new_suffix"))
        assert item.suffix == "new_suffix"
        item.rename_to(Components(extension="new_extension"))
        assert item.extension == "new_extension"

    # Test linked items (with real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"], test_case["real_file"].parent)

        assert isinstance(item, Item)
        assert item.exists is True

        # Test prefix rename
        original_path = Path(item.absolute_path)
        item.rename_to(Components(prefix="new_prefix"))
        assert item.prefix == "new_prefix"
        assert not original_path.exists()
        assert item.exists is True

        # Test delimiter rename
        original_path = Path(item.absolute_path)
        item.rename_to(Components(delimiter="_"))
        assert item.delimiter == "_"
        if not data["delimiter"] == "_":
            assert not original_path.exists()
        assert item.exists is True

        original_path = Path(item.absolute_path)
        item.rename_to(Components(delimiter="-"))
        assert item.delimiter == "-"
        assert not original_path.exists()
        assert item.exists is True

        # Test padding rename
        original_path = Path(item.absolute_path)
        new_padding = 5
        min_padding = len(str(data["frame_number"]))
        item.rename_to(Components(padding=new_padding))
        expected_padding = max(new_padding, min_padding)
        assert item.padding == expected_padding
        if expected_padding != len(item.frame_string):
            assert not original_path.exists()
        assert item.exists is True

        # Test suffix and extension rename
        original_path = Path(item.absolute_path)
        item.rename_to(Components(suffix="new_suffix"))
        assert item.suffix == "new_suffix"
        assert not original_path.exists()
        assert item.exists is True

        original_path = Path(item.absolute_path)
        item.rename_to(Components(extension="new_extension"))
        assert item.extension == "new_extension"
        assert not original_path.exists()
        assert item.exists is True