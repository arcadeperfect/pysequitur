from pysequitur.file_sequence import Item, Parser, Components
from pathlib import Path
import pytest
def test_Item_checkRename(create_files_from_list):
    files = ['source.0001.jpg', 'source_2.0001.jpg']
    file = create_files_from_list(files)[0]
    item = Parser.item_from_filename(file)
    assert item.exists is True
    
    item.rename_to(Components(prefix='source_3'))
    assert item.exists is True

    assert item.check_rename(Components(prefix='source_2'))[2] == True

    # with pytest.raises(FileExistsError):
    #     item.rename(Components(prefix='source_2'))