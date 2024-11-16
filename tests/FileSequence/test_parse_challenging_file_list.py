from pysequitur.file_sequence import FileSequence, SequenceExistence
from pathlib import Path


def test_parse_challenging_file_list(parse_jumble_yaml):
    
    print("test_parse_challenging_file_list")
    
    parsed = parse_jumble_yaml()
    
    print(parsed[0]['files'])
    # sequences = FileSequence.find_sequences_in_filename_list(parsed['files'])
    
    
    for dataset in parse_jumble_yaml():
        sequences = FileSequence.find_sequences_in_filename_list(dataset['files'])
        # print(len(sequences))
        assert len(sequences) == dataset['expected_sequence_count']