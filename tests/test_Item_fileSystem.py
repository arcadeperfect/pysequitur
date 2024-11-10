from pathlib import Path
from pysequitur.file_sequence import Item, Parser, Components
import pytest
import os

def test_item_file_system(create_files_from_list):

    item = Parser.item_from_filename('frame.0001.png')

    # with pytest.raises(FileNotFoundError):
    #     item.delete()
    
    # with pytest.raises(FileNotFoundError):
    #     item.move('test')

    # with pytest.raises(FileNotFoundError):
    #     item.rename('test')

    assert item.exists == False


    

    files = ['frame.0001.png', 
             'frame#$%^e_0002.png',
             'frame0003_post.png',
             '004.png',]

    paths = create_files_from_list(files)


    # -------------- test ----------------- #

    path = paths[0]
    item = Parser.item_from_filename(path)

    assert item.exists is True
    assert item.directory == path.parent
    assert item.filename == path.name



    item.rename('renamed')


    assert item.prefix == 'renamed'
    assert item.filename == 'renamed.0001.png'


    item.delete()
    assert item.exists is False

    # -------------- test ----------------- #

    path = paths[1]
    item = Parser.item_from_filename(path)

    assert item.exists == True    
    assert item.directory == path.parent
    assert item.filename == path.name

    item.rename('renamed')

    assert item.prefix == 'renamed'
    assert item.filename == 'renamed_0002.png'

    item.delete()
    assert item.exists == False


    # -------------- test ----------------- #

    path = paths[2]
    item = Parser.item_from_filename(path)

    assert item.exists == True    
    assert item.directory == path.parent
    assert item.filename == path.name

    item.rename('renamed')

    assert item.prefix == 'renamed'
    assert item.filename == 'renamed0003_post.png'

    item.delete()
    assert item.exists == False


    # -------------- test ----------------- #

    path = paths[3]
    item = Parser.item_from_filename(path)

    assert item.exists == True    
    assert item.directory == path.parent
    assert item.filename == path.name
    

    item.rename('renamed')

    assert item.prefix == 'renamed'
    assert item.filename == 'renamed004.png'

    item.delete()
    assert item.exists == False
    

    # -------------- new data ----------------- #


    files = ['frame.0001.png', 
             'frame#$%^e_0002.png',
             'frame0003_post.png',
             '004.png',]

    paths = create_files_from_list(files)

    # -------------- test ----------------- #
    # empty renamer should have no effect

    path = paths[0]
    item = Parser.item_from_filename(path)

    assert item.exists == True    
    assert item.directory == path.parent
    assert item.filename == path.name
    
    renamer = Components()
    item.rename(renamer)

    assert item.prefix == "frame"
    assert item.filename == "frame.0001.png"
    assert item.delimiter == "."
    assert item.extension == "png"
   

    # -------------- test ----------------- #

    path = paths[0]

    item = Parser.item_from_filename(path)

    renamer = Components(prefix="renamed")
    item.rename(renamer)

    assert item.prefix == "renamed"
    assert item.filename == "renamed.0001.png"
    assert item.delimiter == "."
    assert item.extension == "png"

    renamer = Components(delimiter=r"_")
    item.rename(renamer)

    assert item.prefix == "renamed"
    assert item.filename == "renamed_0001.png"
    assert item.delimiter == "_"
    assert item.extension == "png"

    renamer = Components(extension="jpg")
    item.rename(renamer)

    assert item.prefix == "renamed"
    assert item.filename == "renamed_0001.jpg"
    assert item.delimiter == "_"
    assert item.extension == "jpg"

    renamer = Components(suffix="_post")
    item.rename(renamer)

    assert item.prefix == "renamed"
    assert item.filename == "renamed_0001_post.jpg"
    assert item.delimiter == "_"
    assert item.extension == "jpg"

    renamer = Components(padding=3)
    item.rename(renamer)

    assert item.prefix == "renamed"
    assert item.filename == "renamed_001_post.jpg"
    assert item.delimiter == "_"
    assert item.extension == "jpg"

    renamer = Components(prefix = "renamed_again", 
                      delimiter=".",
                      padding=5, 
                      suffix="_newPost",
                      extension="exr")
    
    item.rename(renamer)

    assert item.prefix == "renamed_again"
    assert item.filename == "renamed_again.00001_newPost.exr"
    assert item.padding == 5
    assert item.delimiter == "."
    assert item.extension == "exr"

    item.delete()

    for path in paths[1:]:
        item = Parser.item_from_filename(path)
        item.delete()

    # -------------- new data ----------------- #


    files = [
        # Basic patterns with different separators
        'frame.0001.png',
        'frame_0002.png',
        'frame-0003.png',
        'frame@0004.png',
        'frame#0005.png',
        
        # Special characters in name
        'frame#$%^e_0006.png',
        'comp@#$%_0007.png',
        'shot&&*_0008.png',
        'render!@#_0009.png',
        'output$$$_0010.png',
        
        # Post numerals
        'frame0011_post.png',
        'frame0012_v1.png',
        'frame0013_final.png',
        'frame0014_approved.png',
        'frame0015_wip.png',
        
        # Different padding lengths
        '0016.png',
        '00017.png',
        '000018.png',
        '0000019.png',
        '00000020.png',
        
        # Mixed case and numbers in name
        'Frame0021.png',
        'FRAME0022.png',
        'frame123_0023.png',
        'Frame456_0024.png',
        'COMP789_0025.png',
        
        # Multiple special characters
        'frame@#$_0026.png',
        'render%^&_0027.png',
        'shot*()_0028.png',
        'output+++_0029.png',
        'comp===_0030.png',
        
        # Different extensions
        'frame_0031.jpg',
        'frame_0032.exr',
        'frame_0033.tiff',
        'frame_0034.dpx',
        'frame_0035.mov',
        
        # Combined post numerals and special characters
        'frame#$%_0036_final.png',
        'comp@@@_0037_v2.png',
        'shot***_0038_approved.png',
        'render$$$_0039_wip.png',
        'output%%%_0040_latest.png',
        
        # No separator variations
        'frame0041.png',
        'FRAME0042.png',
        'render0043.png',
        'comp0044.png',
        'shot0045.png',
        
        # Complex combinations
        'frame#$%_0046_v3_final.png',
        'COMP@@@_0047_latest_approved.png',
        'Shot***_0048_wip_v2.png',
        'Render$$$_0049_final_approved.png',
        'OUTPUT%%%_0050_v4_wip.png'
    ]

    paths = create_files_from_list(files)
    directory = paths[0].parent
    new_directory = directory / "renamed"
    os.mkdir(new_directory)


    # -------------- test ----------------- #
    # test moving files
    for path in paths:
        item = Parser.item_from_filename(path)

        item.move(new_directory)

        assert item.exists is True   
        assert item.directory == new_directory
        assert str(item.filename) == str(path.name)

        new_path_object = Path(str(item.path))
        assert new_path_object.exists() is True
        item.delete()