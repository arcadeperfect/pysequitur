from pysequitur.file_sequence import FileSequence, SequenceExistence, SequenceFactory


def test_parse_similar_sequences_with_different_padding():
    files = ["file.0001.exr", "file.001.exr"]

    sequences = SequenceFactory.from_filenames(files)

    assert len(sequences) == 0

    files = [
        "file.0001.exr",
        "file.0003.exr",
        "file.002.exr",
    ]

    sequences = SequenceFactory.from_filenames(files)

    assert len(sequences) == 1
    assert sequences[0].padding == 4
    assert sequences[0].frame_count == 3

    files = [
        "file.0001.exr",
        "file.0002.exr",
        "file.0003.exr",
        "file.001.exr",
        "file.002.exr",
        "file.003.exr",
        "file.004.exr",
    ]

    sequences = SequenceFactory.from_filenames(files)

    assert len(sequences) == 2
    assert sequences[0].padding == 3
    assert sequences[0].frame_count == 4
    assert sequences[1].padding == 4
    assert sequences[1].frame_count == 3

    files = [
        "file.0001.exr",
        "file.0002.exr",
        "file.0003.exr",
        "file.001.exr",
        "file.002.exr",
        "file.003.exr",
        "file.0004.exr",
    ]

    sequences = SequenceFactory.from_filenames(files)

    assert len(sequences) == 2
    assert sequences[0].padding == 4
    assert sequences[0].frame_count == 4
    assert sequences[1].padding == 3
    assert sequences[1].frame_count == 3

    files = [
        "file.0001.exr",
        "file.002.exr",
        "file.00003.exr",
        "file.04.exr",
        "file.000030.exr",
        "file.000031.exr",
        "file.000032.exr",
    ]

    sequences = SequenceFactory.from_filenames(files)

    # TODO this ideally should parse the sequence starting at 000030 as a separate sequence
    # on the basis that it has different padding to any of the members of the first sequence
    # and is not consecutive
