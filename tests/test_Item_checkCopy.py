from pysequitur.file_sequence import Item, Parser, Components
from pathlib import Path
import pytest
def test_Item_checkCpoy(create_files_from_list):
    files = ['source.0001.jpg', 'source_copy.0001.jpg']
    file = create_files_from_list(files)[0]
    item = Parser.item_from_filename(file)
    assert item.exists is True
    # print(item.check_copy())
    item.check_copy()
    assert item.exists is True

    assert item.check_copy()[2] is True

    assert item.check_copy('source_copy')[2] is True

    with pytest.raises(FileExistsError):
        item.copy()
    
    with pytest.raises(FileExistsError):
        item.copy(Components(prefix='source_copy'))