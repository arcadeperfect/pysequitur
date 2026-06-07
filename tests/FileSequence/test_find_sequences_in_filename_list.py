import pytest
from pysequitur.file_sequence import FileSequence, SequenceExistence, SequenceFactory
from pathlib import Path
import os


def test_find_sequences_in_filename_list(parse_sequence_yaml):
    """Test sequence parsing for both unlinked and linked sequences"""
    test_env_list = parse_sequence_yaml()

    # Test unlinked sequences (without path)
    for case in test_env_list:
        # sequences = FileSequence.find_sequences_in_filename_list(case["files"])
        sequences = SequenceFactory.from_filenames(case["files"]) 
        error_context = f"Failed in case with prefix {case['prefix']}"

        assert len(sequences) == 1, (
            f"Expected 1 sequence but found {len(sequences)}. {error_context}"
        )
        sequence = sequences[0]

        assert sequence.exists == SequenceExistence.FALSE
        assert sequence.prefix == case["prefix"]
        assert sequence.first_frame == case["first_frame"]
        assert sequence.last_frame == case["last_frame"]
        assert sequence.extension == case["extension"]
        assert sequence.delimiter == case["delimiter"]
        assert sequence.suffix == case["suffix"] or (
            sequence.suffix is None and case["suffix"] == ""
        )
        assert sequence.existing_frames == case["existing_frames"]
        assert sequence.missing_frames == case["missing_frames"]
        assert sequence.frame_count == case["frames_count"]
        assert sequence.padding == case["padding"]

    # Test linked sequences (with path)
    for case in test_env_list:
        path = Path(case["tmp_dir"]).joinpath(*Path(case["path"]).parts[1:])

        sequences = SequenceFactory.from_filenames(case["files"], directory = path)
        error_context = f"Failed in case with prefix {case['prefix']}"

        assert len(sequences) == 1, (
            f"Expected 1 sequence but found {len(sequences)}. {error_context}"
        )
        sequence = sequences[0]

        assert sequence.exists == SequenceExistence.TRUE
        assert sequence.prefix == case["prefix"]
        assert sequence.first_frame == case["first_frame"]
        assert sequence.last_frame == case["last_frame"]
        assert sequence.extension == case["extension"]
        assert sequence.delimiter == case["delimiter"]
        assert sequence.suffix == case["suffix"] or (
            sequence.suffix is None and case["suffix"] == ""
        )
        assert sequence.existing_frames == case["existing_frames"]
        assert sequence.missing_frames == case["missing_frames"]
        assert sequence.frame_count == case["frames_count"]
        assert sequence.padding == case["padding"]
