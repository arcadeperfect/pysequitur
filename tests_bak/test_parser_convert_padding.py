from pathlib import Path
from pysequitur.file_sequence import FileSequence, FileSequence, Components, ItemParser
import os



def test_convert_padding():

    # test conversions

    s = "render.%04d.exr"
    t = "render.####.exr"
    assert ItemParser.convert_padding_to_hashes(s) == t
    s = "render.%05d.exr"
    t = "render.#####.exr"
    assert ItemParser.convert_padding_to_hashes(s) == t
    s = "render.%03d.exr"
    t = "render.###.exr"
    assert ItemParser.convert_padding_to_hashes(s) == t
    s = "render.%04d.suffix.exr"
    t = "render.####.suffix.exr"
    assert ItemParser.convert_padding_to_hashes(s) == t
    s = "render_%04d.exr"
    t = "render_####.exr"
    assert ItemParser.convert_padding_to_hashes(s) == t
    s = "render%04d.exr"
    t = "render####.exr"
    assert ItemParser.convert_padding_to_hashes(s) == t
    s = "render%04d_suffix.exr"
    t = "render####_suffix.exr"
    assert ItemParser.convert_padding_to_hashes(s) == t


    # should not change if already in hash notation

    t = "render.####.exr"
    assert ItemParser.convert_padding_to_hashes(t) == t

    t = "render.#####.exr"
    assert ItemParser.convert_padding_to_hashes(t) == t

    t = "render.###.exr"
    assert ItemParser.convert_padding_to_hashes(t) == t

    t = "render.####.suffix.exr"
    assert ItemParser.convert_padding_to_hashes(t) == t

    t = "render_####.exr"
    assert ItemParser.convert_padding_to_hashes(t) == t

    t = "render####.exr"
    assert ItemParser.convert_padding_to_hashes(t) == t

    t = "render####_suffix.exr"
    assert ItemParser.convert_padding_to_hashes(t) == t


