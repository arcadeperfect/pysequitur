import pytest
from pysequitur.file_sequence import FileSequence, SequenceExistence
from pathlib import Path
import os

def test_single_sequence_in_directory(parse_sequence_yaml):
    """Test finding individual sequences in their respective directories"""
    test_env_list = parse_sequence_yaml()
    
    # Verify files were created correctly
    for case in test_env_list:
        for file in case['real_files']:
            assert file.exists(), f"Test file {file} was not created properly"

    # Test sequences in their individual directories
    for case in test_env_list:
        path = Path(case['tmp_dir']).joinpath(*Path(case['path']).parts[1:])
        sequences = FileSequence.find_sequences_in_path(path)
        
        error_context = f"Failed in case with prefix {case['prefix']}"
        assert len(sequences) == 1, f"Expected 1 sequence but found {len(sequences)}. {error_context}"
        
        sequence = sequences[0]
        assert sequence.exists == SequenceExistence.TRUE
        assert sequence.prefix == case['prefix'], error_context
        assert sequence.first_frame == case['first_frame'], error_context
        assert sequence.last_frame == case['last_frame'], error_context
        assert sequence.extension == case['extension'], error_context
        assert sequence.delimiter == case['delimiter'], error_context
        assert sequence.suffix == case['suffix'], error_context
        assert sequence.existing_frames == case['existing_frames'], error_context
        assert sequence.missing_frames == case['missing_frames'], error_context
        assert sequence.frame_count == case['frames_count'], error_context
        assert sequence.padding == case['padding'], error_context

def test_multiple_sequences_in_directory(parse_sequence_yaml):
    """Test finding multiple sequences in a single directory"""
    test_env_list = parse_sequence_yaml()
    
    # Create a directory with all test sequences
    all_files = []
    for case in test_env_list:
        all_files.extend(case['files'])

    combined_dir = Path(test_env_list[0]['tmp_dir']) / "all_files"
    combined_dir.mkdir(exist_ok=True, parents=True)
    
    # Create all files in the combined directory
    for file in all_files:
        new_file = combined_dir / Path(file).name
        new_file.touch()
        assert new_file.exists(), f"Failed to create test file {new_file}"

    # Find and verify sequences
    sequences = FileSequence.find_sequences_in_path(combined_dir)
    assert len(sequences) == len(test_env_list), (
        f"Expected {len(test_env_list)} sequences but found {len(sequences)}"
    )

    # Verify each sequence matches one of the test cases
    for sequence in sequences:
        assert sequence.exists == SequenceExistence.TRUE
        
        # Check that sequence properties match one of the test cases
        matching_cases = [
            case for case in test_env_list
            if (sequence.prefix == case['prefix'] and
                sequence.first_frame == case['first_frame'] and
                sequence.last_frame == case['last_frame'] and
                sequence.extension == case['extension'] and
                sequence.delimiter == case['delimiter'] and
                sequence.suffix == case['suffix'] and
                sequence.existing_frames == case['existing_frames'] and
                sequence.missing_frames == case['missing_frames'] and
                sequence.frame_count == case['frames_count'] and
                sequence.padding == case['padding'])
        ]
        
        assert len(matching_cases) == 1, (
            f"Sequence {sequence.prefix} did not match exactly one test case"
        )

# from posix import mkdir
# from pysequitur.file_sequence import FileSequence, SequenceExistence
# from pathlib import Path
# import os
# def test_filesequence_from_directory(parse_sequence_yaml):

#     print("test_filesequence")
#     filename = "1.yaml"
#     cases = parse_sequence_yaml(Path(__file__).parent / 'test_data' / filename)

#     for case in cases:
#         for file in case['real_files']:
#             assert file.exists()


#     # linked

#     for case in cases:

#         path = Path(case['tmp_dir']).joinpath(*Path(case['path']).parts[1:])
#         sequences = FileSequence.find_sequences_in_path(path)
#         sequences = FileSequence.find_sequences_in_filename_list(os.listdir(path), path)
#         assert len(sequences) == 1
#         sequence = sequences[0]

#         assert sequence.exists == SequenceExistence.TRUE
#         assert sequence.prefix == case['prefix']
#         assert sequence.first_frame == case['first_frame']
#         assert sequence.last_frame == case['last_frame']
#         assert sequence.extension == case['extension']
#         assert sequence.delimiter == case['delimiter']
#         assert sequence.suffix == case['suffix']
#         assert sequence.existing_frames == case['existing_frames']
#         assert sequence.missing_frames == case['missing_frames']
#         assert sequence.frame_count == case['frames_count']
#         assert sequence.padding == case['padding']

#     all_files = []
#     for case in cases:
#         all_files.extend(case['files'])

#     dir = Path(cases[0]['tmp_dir'])/"all_files"
#     dir.mkdir(exist_ok=True, parents=True)
#     assert dir.is_dir()
#     assert dir.exists()

#     for file in all_files:
#         new_file = dir/Path(file).name
#         new_file.touch()
#         assert new_file.exists()

#     sequences = FileSequence.find_sequences_in_path(dir)

#     assert len(sequences) == len(cases)

#     for sequence in sequences:
#         assert sequence.exists == SequenceExistence.TRUE
#         assert sequence.prefix in [case['prefix'] for case in cases]
#         assert sequence.first_frame in [case['first_frame'] for case in cases]
#         assert sequence.last_frame in [case['last_frame'] for case in cases]
#         assert sequence.extension in [case['extension'] for case in cases]
#         assert sequence.delimiter in [case['delimiter'] for case in cases]
#         assert sequence.suffix in [case['suffix'] for case in cases]
#         assert sequence.existing_frames in [case['existing_frames'] for case in cases]
#         assert sequence.missing_frames in [case['missing_frames'] for case in cases]
#         assert sequence.frame_count in [case['frames_count'] for case in cases]
#         assert sequence.padding in [case['padding'] for case in cases]
