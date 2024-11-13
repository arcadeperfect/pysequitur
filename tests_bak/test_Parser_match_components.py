from pathlib import Path
from pysequitur.file_sequence import FileSequence, FileSequence, Components
import os


def test_parse_filename():

    files = [
    # Base sequences
    'frame.0001.png', 'frame.0002.png', 'frame.0003.png', 'frame.0004.png', 'frame.0005.png',
    'frame.0001.jpg', 'frame.0002.jpg', 'frame.0003.jpg', 'frame.0004.jpg', 'frame.0005.jpg',
    'frame_0001.jpg', 'frame_0002.jpg', 'frame_0003.jpg', 'frame_0004.jpg', 'frame_0005.jpg',
    'image.0001.exr', 'image.0002.exr', 'image.0003.exr', 'image.0004.exr', 'image.0005.exr',
    'render.1001.png', 'render.1002.png', 'render.1003.png', 'render.1004.png', 'render.1005.png',

    # Additional test sequences
    'comp_v001.0001.dpx', 'comp_v001.0002.dpx', 'comp_v001.0003.dpx',
    'comp_v002.0001.dpx', 'comp_v002.0002.dpx', 'comp_v002.0003.dpx',
    'shot_010_0001.tif', 'shot_010_0002.tif', 'shot_010_0003.tif',
    'shot_020_0001.tif', 'shot_020_0002.tif', 'shot_020_0003.tif',
    'BG.01.tga', 'BG.02.tga', 'BG.03.tga',
    'BG.01.jpg', 'BG.02.jpg', 'BG.03.jpg',
    'render.0001.beauty.exr', 'render.0002.beauty.exr', 'render.0003.beauty.exr',
    'render.0001.spec.exr', 'render.0002.spec.exr', 'render.0003.spec.exr'
]

    sequences = FileSequence.match_components_in_filename_list(Components(), files)

    print("\n----")

    for s in sequences:
        # print(s.prefix)
        if s.prefix == "render" and s.extension == "exr":
            print(s)

    # Basic component matching tests
    sequences = FileSequence.match_components_in_filename_list(Components(), files)
    assert len(sequences) == 13  # All sequences

    sequences = FileSequence.match_components_in_filename_list(Components(prefix="frame"), files)
    assert len(sequences) == 3  # frame.*.png, frame.*.jpg, frame_*.jpg

    sequences = FileSequence.match_components_in_filename_list(Components(extension="exr"), files)
    # image.*.exr, render.*.beauty.exr, render.*.spec.exr
    assert len(sequences) == 3

    # File extension tests
    sequences = FileSequence.match_components_in_filename_list(Components(extension="dpx"), files)
    assert len(sequences) == 2  # comp_v001.*.dpx, comp_v002.*.dpx

    sequences = FileSequence.match_components_in_filename_list(Components(extension="tif"), files)
    assert len(sequences) == 2  # shot_010_*.tif, shot_020_*.tif

    sequences = FileSequence.match_components_in_filename_list(Components(extension="tga"), files)
    assert len(sequences) == 1  # BG.*.tga

    # Prefix matching tests
    sequences = FileSequence.match_components_in_filename_list(Components(prefix="render"), files)
    assert len(sequences) == 3 

    sequences = FileSequence.match_components_in_filename_list(Components(prefix="BG"), files)
    assert len(sequences) == 2  # BG.*.tga, BG.*.jpg

    # Delimiter tests
    sequences = FileSequence.match_components_in_filename_list(Components(delimiter="."), files)
    assert len(sequences) == 10  # All sequences with dot delimiter

    sequences = FileSequence.match_components_in_filename_list(Components(delimiter="_"), files)
    assert len(sequences) == 3  # All sequences with underscore delimiter

    # Combined criteria tests
    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="render", extension="exr"), files)
    assert len(sequences) == 2 

    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="frame", delimiter="."), files)
    assert len(sequences) == 2

    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="render", suffix=".beauty"), files)
    assert len(sequences) == 1  # render.*.beauty.exr

    # Suffix tests
    sequences = FileSequence.match_components_in_filename_list(Components(suffix=".beauty"), files)
    assert len(sequences) == 1  # render.*.beauty.exr

    sequences = FileSequence.match_components_in_filename_list(Components(suffix=".spec"), files)
    assert len(sequences) == 1  # render.*.spec.exr

    # Multiple criteria tests
    sequences = FileSequence.match_components_in_filename_list(Components(
        prefix="render", extension="exr", suffix=".beauty"), files)
    assert len(sequences) == 1  # render.*.beauty.exr

    sequences = FileSequence.match_components_in_filename_list(Components(
        prefix="frame", delimiter="_", extension="jpg"), files)
    assert len(sequences) == 1  # shot_010_*.tif, shot_020_*.tif

    # Exclusive tests
    sequences = FileSequence.match_components_in_filename_list(Components(
        prefix="frame", extension="png", delimiter="."), files)
    assert len(sequences) == 1  # Only frame.*.png

    sequences = FileSequence.match_components_in_filename_list(Components(
        prefix="BG", extension="tga", delimiter="."), files)
    assert len(sequences) == 1  # Only BG.*.tga

    # No match tests
    sequences = FileSequence.match_components_in_filename_list(Components(prefix="nonexistent"), files)
    assert len(sequences) == 0

    sequences = FileSequence.match_components_in_filename_list(Components(extension="missing"), files)
    assert len(sequences) == 0

    sequences = FileSequence.match_components_in_filename_list(Components(suffix="none"), files)
    assert len(sequences) == 0

    # Multiple criteria no match tests
    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="frame", extension="exr"), files)
    assert len(sequences) == 0

    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="render", extension="jpg"), files)
    assert len(sequences) == 0

    # Mixed valid/invalid criteria tests
    sequences = FileSequence.match_components_in_filename_list(Components(
        prefix="frame", extension="invalid"), files)
    assert len(sequences) == 0

    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="invalid", extension="png"), files)
    assert len(sequences) == 0

    # Case sensitivity tests
    sequences = FileSequence.match_components_in_filename_list(Components(prefix="BG"), files)
    assert len(sequences) == 2  # BG.*.tga, BG.*.jpg

    sequences = FileSequence.match_components_in_filename_list(Components(prefix="bg"), files)
    assert len(sequences) == 0  # Case sensitive

    # Padding tests (assuming consistent padding in sequences)
    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="frame", padding=4), files)
    assert len(sequences) == 3  # All frame sequences use 4-digit padding

    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="render", padding=4), files)
    assert len(sequences) == 3  # render.*.png and render.*.{beauty,spec}.exr

    # Combined criteria with padding
    sequences = FileSequence.match_components_in_filename_list(Components(
        prefix="frame", padding=4, extension="png"), files)
    assert len(sequences) == 1  # frame.####.png

    sequences = FileSequence.match_components_in_filename_list(Components(
        prefix="render", padding=4, suffix=".beauty"), files)
    assert len(sequences) == 1  # render.####.beauty.exr

    # Multiple delimiters test
    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="comp", delimiter="_"), files)
    assert len(sequences) == 0  # comp_v001.*.dpx, comp_v002.*.dpx

    
    
    
    
    ####### SAME TESTS VIA FILESEQUENCE CLASS #######

    sequences = FileSequence.match_components_in_filename_list(Components(), files)

    print("\n----")

    for s in sequences:
        # print(s.prefix)
        if s.prefix == "render" and s.extension == "exr":
            print(s)

    # Basic component matching tests
    sequences = FileSequence.match_components_in_filename_list(Components(), files)
    assert len(sequences) == 13  # All sequences

    sequences = FileSequence.match_components_in_filename_list(Components(prefix="frame"), files)
    assert len(sequences) == 3  # frame.*.png, frame.*.jpg, frame_*.jpg

    sequences = FileSequence.match_components_in_filename_list(Components(extension="exr"), files)
    # image.*.exr, render.*.beauty.exr, render.*.spec.exr
    assert len(sequences) == 3

    # File extension tests
    sequences = FileSequence.match_components_in_filename_list(Components(extension="dpx"), files)
    assert len(sequences) == 2  # comp_v001.*.dpx, comp_v002.*.dpx

    sequences = FileSequence.match_components_in_filename_list(Components(extension="tif"), files)
    assert len(sequences) == 2  # shot_010_*.tif, shot_020_*.tif

    sequences = FileSequence.match_components_in_filename_list(Components(extension="tga"), files)
    assert len(sequences) == 1  # BG.*.tga

    # Prefix matching tests
    sequences = FileSequence.match_components_in_filename_list(Components(prefix="render"), files)
    assert len(sequences) == 3 

    sequences = FileSequence.match_components_in_filename_list(Components(prefix="BG"), files)
    assert len(sequences) == 2  # BG.*.tga, BG.*.jpg

    # Delimiter tests
    sequences = FileSequence.match_components_in_filename_list(Components(delimiter="."), files)
    assert len(sequences) == 10  # All sequences with dot delimiter

    sequences = FileSequence.match_components_in_filename_list(Components(delimiter="_"), files)
    assert len(sequences) == 3  # All sequences with underscore delimiter

    # Combined criteria tests
    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="render", extension="exr"), files)
    assert len(sequences) == 2 

    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="frame", delimiter="."), files)
    assert len(sequences) == 2

    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="render", suffix=".beauty"), files)
    assert len(sequences) == 1  # render.*.beauty.exr

    # Suffix tests
    sequences = FileSequence.match_components_in_filename_list(Components(suffix=".beauty"), files)
    assert len(sequences) == 1  # render.*.beauty.exr

    sequences = FileSequence.match_components_in_filename_list(Components(suffix=".spec"), files)
    assert len(sequences) == 1  # render.*.spec.exr

    # Multiple criteria tests
    sequences = FileSequence.match_components_in_filename_list(Components(
        prefix="render", extension="exr", suffix=".beauty"), files)
    assert len(sequences) == 1  # render.*.beauty.exr

    sequences = FileSequence.match_components_in_filename_list(Components(
        prefix="frame", delimiter="_", extension="jpg"), files)
    assert len(sequences) == 1  # shot_010_*.tif, shot_020_*.tif

    # Exclusive tests
    sequences = FileSequence.match_components_in_filename_list(Components(
        prefix="frame", extension="png", delimiter="."), files)
    assert len(sequences) == 1  # Only frame.*.png

    sequences = FileSequence.match_components_in_filename_list(Components(
        prefix="BG", extension="tga", delimiter="."), files)
    assert len(sequences) == 1  # Only BG.*.tga

    # No match tests
    sequences = FileSequence.match_components_in_filename_list(Components(prefix="nonexistent"), files)
    assert len(sequences) == 0

    sequences = FileSequence.match_components_in_filename_list(Components(extension="missing"), files)
    assert len(sequences) == 0

    sequences = FileSequence.match_components_in_filename_list(Components(suffix="none"), files)
    assert len(sequences) == 0

    # Multiple criteria no match tests
    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="frame", extension="exr"), files)
    assert len(sequences) == 0

    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="render", extension="jpg"), files)
    assert len(sequences) == 0

    # Mixed valid/invalid criteria tests
    sequences = FileSequence.match_components_in_filename_list(Components(
        prefix="frame", extension="invalid"), files)
    assert len(sequences) == 0

    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="invalid", extension="png"), files)
    assert len(sequences) == 0

    # Case sensitivity tests
    sequences = FileSequence.match_components_in_filename_list(Components(prefix="BG"), files)
    assert len(sequences) == 2  # BG.*.tga, BG.*.jpg

    sequences = FileSequence.match_components_in_filename_list(Components(prefix="bg"), files)
    assert len(sequences) == 0  # Case sensitive

    # Padding tests (assuming consistent padding in sequences)
    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="frame", padding=4), files)
    assert len(sequences) == 3  # All frame sequences use 4-digit padding

    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="render", padding=4), files)
    assert len(sequences) == 3  # render.*.png and render.*.{beauty,spec}.exr

    # Combined criteria with padding
    sequences = FileSequence.match_components_in_filename_list(Components(
        prefix="frame", padding=4, extension="png"), files)
    assert len(sequences) == 1  # frame.####.png

    sequences = FileSequence.match_components_in_filename_list(Components(
        prefix="render", padding=4, suffix=".beauty"), files)
    assert len(sequences) == 1  # render.####.beauty.exr

    # Multiple delimiters test
    sequences = FileSequence.match_components_in_filename_list(
        Components(prefix="comp", delimiter="_"), files)
    assert len(sequences) == 0  # comp_v001.*.dpx, comp_v002.*.dpx

