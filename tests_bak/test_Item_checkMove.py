from pysequitur.file_sequence import Item, Parser
from pathlib import Path
import pytest
def test_Item_checkMove(create_files_from_list):
    files = ['source.0001.jpg']
    file = create_files_from_list(files)[0]
    file_dir = Path(file).parent

    new_dir = Path(file_dir / 'moved')
    new_dir.mkdir()
    new_file = new_dir / Path(file).name
    new_file.touch()


    item = Parser.item_from_filename(file)

    assert item.check_move(new_dir)[2] is True
    

    with pytest.raises(FileExistsError):
        item.move_to(new_dir)
