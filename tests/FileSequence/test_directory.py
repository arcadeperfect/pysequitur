from pysequitur import FileSequence, Components
from pathlib import Path



def test_directory(parse_sequence_yaml):
    
    test_env = parse_sequence_yaml()
 
    for case in test_env:
        path = Path(case['tmp_dir']).joinpath(*Path(case['path']).parts[1:])
        sequences = FileSequence.find_sequences_in_path(path)
        for sequence in sequences:
            assert sequence.directory == path