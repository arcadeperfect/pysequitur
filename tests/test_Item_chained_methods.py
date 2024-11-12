from pysequitur.file_sequence import FileSequence, Parser, Components
import os

def test_item_chained_methods(create_files_from_list):




    files = ['frame.0001.png', 
             'frame#$%^e_0002.png',
             'frame0003_post.png',
             '004.png',]

    test_env = create_files_from_list(files)

    dir = test_env[0].parent

    sub_dir = dir / 'sub_dir'
    sub_dir.mkdir()



    

    for file in test_env:

        item = Parser.item_from_path(file)

        assert item.exists is True

        copied_item = item.rename(Components(prefix='renamed')).move(sub_dir).copy()

        assert item.prefix == 'renamed'
        assert item.directory == sub_dir
        assert copied_item.exists is True
        assert copied_item.directory == sub_dir
        assert copied_item.prefix == item.prefix + '_copy'

        item.rename(Components(prefix='renamed2')).delete()
        assert item.exists is False
        copied_item.delete()
        assert copied_item.exists is False