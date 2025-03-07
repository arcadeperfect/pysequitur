import pytest
from pathlib import Path
from pysequitur import Item


def test_item_check_move(parse_item_yaml):
    test_env_list = parse_item_yaml()

    # Test unlinked items (no real file associated)
    for test_case in test_env_list:
        data = test_case["data"]
        item = Item.from_file_name(data["file_name"])

        assert isinstance(item, Item)
        assert item.exists is False

        with pytest.raises(FileNotFoundError):
            item.move_to(Path("imaginary_path"))

    # Test linked items (real file associated)
    for test_case in test_env_list:
        move_to_dir = Path(test_case["tmp_dir"] / "move_to")
        move_to_dir.mkdir(parents=True, exist_ok=True)

        data = test_case["data"]
        item = Item.from_file_name(data["file_name"], test_case["real_file"].parent)

        assert isinstance(item, Item)
        assert item.exists

        # Test initial move check
        check_move = item.check_move(move_to_dir)
        assert check_move[0] == item.absolute_path
        assert check_move[1] == move_to_dir / item.filename
        assert check_move[2] is False

        # Test move check with existing file
        check_move[1].touch()
        check_move = item.check_move(move_to_dir)
        assert check_move[0] == item.absolute_path
        assert check_move[1] == move_to_dir / item.filename
        assert check_move[2] is True

        with pytest.raises(FileExistsError):
            item.move_to(move_to_dir)

        check_move[1].unlink()


# import pytest
# from pathlib import Path
# from pysequitur import Item

# def test_item_check_move(parse_item_yaml):

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

#         assert item.exists

#         check_move = item.check_move(move_to_dir)

#         assert check_move[0] == item.absolute_path
#         assert check_move[1] == move_to_dir / item.filename
#         assert check_move[2] is False

#         check_move[1].touch()

#         check_move = item.check_move(move_to_dir)

#         assert check_move[0] == item.absolute_path
#         assert check_move[1] == move_to_dir / item.filename
#         assert check_move[2] is True

#         with pytest.raises(FileExistsError):
#             item.move_to(move_to_dir)

#         check_move[1].unlink()
