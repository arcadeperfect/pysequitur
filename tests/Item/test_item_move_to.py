import pytest
from pathlib import Path
import shutil
from pysequitur import Item


def test_item_move_to(parse_item_yaml):
    test_env_list = parse_item_yaml()

    # Test unlinked items (no real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"])

        assert isinstance(item, Item)
        assert item.exists is False

        with pytest.raises(FileNotFoundError):
            item.move_to(Path("imaginary_path"))

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

        item.move_to(move_to_dir)

        assert item.exists
        assert item.directory == move_to_dir
        assert not original_path.exists()

        shutil.rmtree(move_to_dir)


# import pytest
# from pathlib import Path
# from pysequitur import Item
# import shutil
# # from pysequitur import Item

# def test_item_move_to(parse_item_yaml):

#     filename = "ItemTestData.yaml"
#     test_env = parse_item_yaml(Path(__file__).parent / 'test_data' / filename)

#     # unlinked items (no real file associated)

#     for test_case in test_env:

#         data = test_case['data']
#         item = Item.from_file_name(data['file_name'])

#         assert isinstance(item, Item)
#         assert item.exists is False

#         with pytest.raises(FileNotFoundError):
#             item.move_to(Path("imginary_path"))


#     # linked items (real file associated)

#     for test_case in test_env:

#         move_to_dir = Path(test_case['tmp_dir'] / 'move_to')
#         move_to_dir.mkdir(parents=True, exist_ok=True)

#         data = test_case['data']
#         item = Item.from_file_name(data['file_name'], test_case['real_file'].parent)


#         assert isinstance(item, Item)

#         original_path = Path(item.absolute_path)
#         assert original_path.exists()
#         assert item.exists

#         item.move_to(move_to_dir)

#         assert item.exists
#         assert item.directory == move_to_dir

#         assert not original_path.exists()

#         shutil.rmtree(move_to_dir)
