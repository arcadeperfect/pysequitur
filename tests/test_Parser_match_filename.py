from pathlib import Path
from pysequitur.file_sequence import FileSequence, FileSequence, Components
import os




def test_match_filename():


    files = ["not_a_sequence.txt",
    "frame.0001.png", "frame.0002.png", "frame.0003.png", "frame.0004.png", "frame.0005.png",
    "frame.0001.jpg", "frame.0002.jpg", "frame.0003.jpg", "frame.0004.jpg", "frame.0005.jpg",
    "frame_0001.jpg", "frame_0002.jpg", "frame_0003.jpg", "frame_0004.jpg", "frame_0005.jpg",
    "render.101_post.png", "render.102_post.png", "render.103_postpng", "render.104_post.png", "render.105_post.png"]

   


    name = "not_a_sequence.txt"
    sequence = FileSequence.from_filename_list(name, files)
    assert sequence is None

    name = "frame.####.png"
    sequence = FileSequence.from_filename_list(name, files)
    assert sequence.prefix == "frame"
    assert sequence.delimiter == "."
    assert sequence.extension == "png"
    assert sequence.padding == 4
    
    name = "frame.####.jpg"
    sequence = FileSequence.from_filename_list(name, files)
    assert sequence.prefix == "frame"
    assert sequence.delimiter == "."
    assert sequence.extension == "jpg"
    assert sequence.padding == 4

    name = "frame_####.jpg"
    sequence = FileSequence.from_filename_list(name, files)
    assert sequence.prefix == "frame"
    assert sequence.delimiter == "_"
    assert sequence.extension == "jpg"
    assert sequence.padding == 4
        
    name = "render.###_post.png"
    sequence = FileSequence.from_filename_list(name, files)
    assert sequence.prefix == "render"
    assert sequence.delimiter == "."
    assert sequence.suffix == "_post"
    assert sequence.extension == "png"
    assert sequence.padding == 3


