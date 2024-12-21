# import pytest
# from pysequitur.file_sequence import FileSequence, SequenceExistence
# from pathlib import Path
# import os


# def test_parse_with_padding_conversion():
    
#     files = [
#         "file.0001.exr",
#         "file.0002.exr",
#         "file.0003.exr",
#         "file.0004.exr",
#     ]

#     seq_string = "file.%04d.exr"

#     sequences = FileSequence.find_sequences_in_filename_list(files, seq_string)

#     assert len(sequences) == 1