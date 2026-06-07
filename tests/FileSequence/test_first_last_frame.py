from pysequitur import FileSequence, Components, SequenceFactory


def test_first_last_frame():
    files = [
        "file.0001.exr",
        "file.0002.exr",
        "file.0003.exr",
        "file.0004.exr",
    ]

    sequences = SequenceFactory.from_filenames(files)
    
    assert len(sequences) == 1
    sequence = sequences[0]

    assert sequence.first_frame == 1
    assert sequence.last_frame == 4

    files = [
        "file.1234.exr",
        "file.1235.exr",
        "file.1278.exr",
        "file.2000.exr",
    ]

    sequences = SequenceFactory.from_filenames(files)
    assert len(sequences) == 1
    sequence = sequences[0]

    assert sequence.first_frame == 1234
    assert sequence.last_frame == 2000
