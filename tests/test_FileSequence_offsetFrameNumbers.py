from pathlib import Path
from pysequitur.file_sequence import Item, Parser, Components
import pytest
import os

def test_offset_frame_numbers(create_files_from_list):

    print("\ntest_offset_frame_numbers ----- ")

    files = ['frame.0001.jpg', 
             'frame.0002.jpg', 
             'frame.0003.jpg', 
             'frame.0004.jpg', 
             'frame.0005.jpg']

    paths = create_files_from_list(files)

    path = paths[0]
    print(path.parent)

    s = Parser.filesequences_from_directory(str(path.parent))[0]

    # print(s)

    assert s.frame_count == 5
    assert s.first_frame == 1
    assert s.last_frame == 5

    s.offset_frames(1)

    assert s.first_frame == 2
    assert s.last_frame == 6

    s.offset_frames(-1)

    assert s.first_frame == 1
    assert s.last_frame == 5

    with pytest.raises(ValueError):
        s.offset_frames(-50)

    assert s.first_frame == 1
    assert s.last_frame == 5

    with pytest.raises(ValueError):
        s.offset_frames(-2)

    assert s.first_frame == 1
    assert s.last_frame == 5

    s.offset_frames(1234)

    assert s.first_frame == 1235
    assert s.last_frame == 1239

    s.offset_frames(-1234)

    assert s.first_frame == 1
    assert s.last_frame == 5

    s.set_padding(1)

    assert s.items[0].frame_string == '1'
    assert s.file_name == 'frame.#.jpg'

    s.set_padding(6)

    assert s.items[0].frame_string == '000001'
    assert s.file_name == 'frame.######.jpg'

    s.set_padding(1)
    s.offset_frames(6)
    
    assert s.first_frame == 7
    assert s.last_frame == 11
    assert s.padding == 2
    assert s.file_name == 'frame.##.jpg'

    s.set_padding(1)
    assert s.first_frame == 7
    assert s.last_frame == 11
    assert s.padding == 2
    assert s.file_name == 'frame.##.jpg'