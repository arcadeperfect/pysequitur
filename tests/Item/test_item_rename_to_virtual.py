import pytest
from pathlib import Path
from pysequitur import Item
from pysequitur.file_sequence import Components


def test_item_rename_virtual(parse_item_yaml):
    test_env_list = parse_item_yaml()

    # Test linked items (with real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"], test_case["real_file"].parent)

        assert isinstance(item, Item)
        assert item.exists is True
        original_path = Path(item.absolute_path)

        # Test virtual prefix rename
        virtual_item = item.rename_to(Components(prefix="new_prefix"), virtual=True)
        assert virtual_item.prefix == "new_prefix"
        assert item.prefix == data["prefix"]  # Original item unchanged
        assert original_path.exists()  # Original file still exists

        # Test virtual delimiter rename
        virtual_item = item.rename_to(Components(delimiter="-"), virtual=True)
        assert virtual_item.delimiter == "-"
        assert item.delimiter == data["delimiter"]  # Original item unchanged
        assert original_path.exists()  # Original file still exists

        # Test virtual padding rename
        new_padding = 5
        virtual_item = item.rename_to(Components(padding=new_padding), virtual=True)
        assert virtual_item.padding == max(new_padding, len(str(data["frame_number"])))
        assert item.padding == data["padding"]  # Original item unchanged
        assert original_path.exists()  # Original file still exists

        # Test virtual suffix rename
        virtual_item = item.rename_to(Components(suffix="new_suffix"), virtual=True)
        assert virtual_item.suffix == "new_suffix"
        assert item.suffix == data["suffix"]  # Original item unchanged
        assert original_path.exists()  # Original file still exists

        # Test virtual extension rename
        virtual_item = item.rename_to(
            Components(extension="new_extension"), virtual=True
        )
        assert virtual_item.extension == "new_extension"
        assert item.extension == data["extension"]  # Original item unchanged
        assert original_path.exists()  # Original file still exists
