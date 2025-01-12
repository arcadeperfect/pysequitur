from pysequitur import FileSequence

def test_parse_sequence_with_padding_conversion():

    files = [
        "file.1001.exr",
        "file.1002.exr",
        "file.1003.exr",
        "file.1004.exr",
    ]

    seq_string = "file.%04d.exr"

    sequence = FileSequence.match_sequence_string_in_filename_list(seq_string, files)
    assert sequence is not None
    assert sequence.padding == 4
    assert sequence.frame_count == 4

    # assert len(sequences) == 1