from pysequitur import FileSequence, Components, SequenceFactory


def test_prefix_extension_delimiter_suffix():
    files = [
        "file.0001_suffix.exr",
        "file.0002_suffix.exr",
        "file.0003_suffix.exr",
        "file.0004_suffix.exr",
    ]

    sequences = SequenceFactory.from_filenames(files)
    assert len(sequences) == 1
    sequence = sequences[0]

    assert sequence.prefix == "file"
    assert sequence.extension == "exr"
    assert sequence.delimiter == "."
    assert sequence.suffix == "_suffix"

    files = [
        "file.0001.exr",
        "file.0002.exr",
        "file.0003.exr",
        "file.0004.exr",
    ]

    sequences = SequenceFactory.from_filenames(files)
    assert len(sequences) == 1
    sequence = sequences[0]

    assert sequence.prefix == "file"
    assert sequence.extension == "exr"
    assert sequence.delimiter == "."
    assert sequence.suffix == ""

    files = [
        "render_0001_beauty.png",
        "render_0002_beauty.png",
        "render_0003_beauty.png",
    ]
    sequences = SequenceFactory.from_filenames(files)
    assert len(sequences) == 1
    sequence = sequences[0]
    assert sequence.prefix == "render"
    assert sequence.extension == "png"
    assert sequence.delimiter == "_"
    assert sequence.suffix == "_beauty"

    files = ["shot-0001-final.jpeg", "shot-0002-final.jpeg", "shot-0003-final.jpeg"]
    sequences = SequenceFactory.from_filenames(files)
    assert len(sequences) == 1
    sequence = sequences[0]
    assert sequence.prefix == "shot"
    assert sequence.extension == "jpeg"
    assert sequence.delimiter == "-"
    assert sequence.suffix == "-final"

    files = [
        "scene_01_shot_03.0001.jpg",
        "scene_01_shot_03.0002.jpg",
        "scene_01_shot_03.0003.jpg",
    ]
    sequences = SequenceFactory.from_filenames(files)
    assert len(sequences) == 1
    sequence = sequences[0]
    assert sequence.prefix == "scene_01_shot_03"
    assert sequence.extension == "jpg"
    assert sequence.delimiter == "."
    assert sequence.suffix == ""

    files = ["data_0001", "data_0002", "data_0003"]
    sequences = SequenceFactory.from_filenames(files)
    assert len(sequences) == 1
    sequence = sequences[0]
    assert sequence.prefix == "data"
    assert sequence.extension == ""
    assert sequence.delimiter == "_"
    assert sequence.suffix == ""

    files = [
        "render@2x_0001_final.png",
        "render@2x_0002_final.png",
        "render@2x_0003_final.png",
    ]
    sequences = SequenceFactory.from_filenames(files)
    assert len(sequences) == 1
    sequence = sequences[0]
    assert sequence.prefix == "render@2x"
    assert sequence.extension == "png"
    assert sequence.delimiter == "_"
    assert sequence.suffix == "_final"

    files = ["SHOT_0001_comp.EXR", "SHOT_0002_comp.EXR", "SHOT_0003_comp.EXR"]
    sequences = SequenceFactory.from_filenames(files)
    assert len(sequences) == 1
    sequence = sequences[0]
    assert sequence.prefix == "SHOT"
    assert sequence.extension == "EXR"
    assert sequence.delimiter == "_"
    assert sequence.suffix == "_comp"
