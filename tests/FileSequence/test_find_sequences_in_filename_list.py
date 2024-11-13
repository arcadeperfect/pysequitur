from pysequitur.file_sequence import FileSequence, SequenceExistence
from pathlib import Path

def test_filesequence_from_file_list(parse_sequence_yaml):

    print("test_filesequence")
    filename = "1.yaml"
    cases = parse_sequence_yaml(Path(__file__).parent / 'test_data' / filename)
    
    for case in cases:
        for file in case['real_files']:
            assert file.exists()
    
    # unlinked
    
    for case in cases:
        
        sequences = FileSequence.find_sequences_in_filename_list(case['files'])
        assert len(sequences) == 1
        sequence = sequences[0]
        assert sequence.exists == SequenceExistence.FALSE
        assert sequence.prefix == case['prefix']
        assert sequence.first_frame == case['first_frame']
        assert sequence.last_frame == case['last_frame']
        assert sequence.extension == case['extension']
        assert sequence.delimiter == case['delimiter']
        assert sequence.suffix == case['suffix']
        assert sequence.existing_frames == case['existing_frames']
        assert sequence.missing_frames == case['missing_frames']
        assert sequence.frame_count == case['frames_count']
        assert sequence.padding == case['padding']

    # linked
    
    for case in cases:
        
        path = Path(case['tmp_dir']).joinpath(*Path(case['path']).parts[1:])
        
        sequences = FileSequence.find_sequences_in_filename_list(case['files'], path)
        assert len(sequences) == 1
        sequence = sequences[0]
    
        assert sequence.exists == SequenceExistence.TRUE
        assert sequence.prefix == case['prefix']
        assert sequence.first_frame == case['first_frame']
        assert sequence.last_frame == case['last_frame']
        assert sequence.extension == case['extension']
        assert sequence.delimiter == case['delimiter']
        assert sequence.suffix == case['suffix']
        assert sequence.existing_frames == case['existing_frames']
        assert sequence.missing_frames == case['missing_frames']
        assert sequence.frame_count == case['frames_count']
        assert sequence.padding == case['padding']