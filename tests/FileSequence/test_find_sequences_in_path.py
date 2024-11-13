from posix import mkdir
from pysequitur.file_sequence import FileSequence, SequenceExistence
from pathlib import Path
import os
def test_filesequence_from_directory(parse_sequence_yaml):

    print("test_filesequence")
    filename = "1.yaml"
    cases = parse_sequence_yaml(Path(__file__).parent / 'test_data' / filename)

    for case in cases:
        for file in case['real_files']:
            assert file.exists()


    # linked

    for case in cases:

        path = Path(case['tmp_dir']).joinpath(*Path(case['path']).parts[1:])
        sequences = FileSequence.find_sequences_in_path(path)
        sequences = FileSequence.find_sequences_in_filename_list(os.listdir(path), path)
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

    all_files = []
    for case in cases:
        all_files.extend(case['files'])

    dir = Path(cases[0]['tmp_dir'])/"all_files"
    dir.mkdir(exist_ok=True, parents=True)
    assert dir.is_dir()
    assert dir.exists()

    for file in all_files:
        new_file = dir/Path(file).name
        new_file.touch()
        assert new_file.exists()

    sequences = FileSequence.find_sequences_in_path(dir)

    assert len(sequences) == len(cases)

    for sequence in sequences:
        assert sequence.exists == SequenceExistence.TRUE
        assert sequence.prefix in [case['prefix'] for case in cases]
        assert sequence.first_frame in [case['first_frame'] for case in cases]
        assert sequence.last_frame in [case['last_frame'] for case in cases]
        assert sequence.extension in [case['extension'] for case in cases]
        assert sequence.delimiter in [case['delimiter'] for case in cases]
        assert sequence.suffix in [case['suffix'] for case in cases]
        assert sequence.existing_frames in [case['existing_frames'] for case in cases]
        assert sequence.missing_frames in [case['missing_frames'] for case in cases]
        assert sequence.frame_count in [case['frames_count'] for case in cases]
        assert sequence.padding in [case['padding'] for case in cases]
