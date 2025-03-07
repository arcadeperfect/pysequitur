import pytest
from pysequitur.file_sequence import FileSequence, SequenceExistence, SequenceFactory
from pathlib import Path
import os


def test_single_sequence_in_directory(parse_sequence_yaml):
    """Test finding individual sequences in their respective directories"""
    test_env_list = parse_sequence_yaml()

    # Verify files were created correctly
    for case in test_env_list:
        for file in case["real_files"]:
            assert file.exists(), f"Test file {file} was not created properly"

    # Test sequences in their individual directories
    for case in test_env_list:
        path = Path(case["tmp_dir"]).joinpath(*Path(case["path"]).parts[1:])
        sequences = SequenceFactory.from_directory(path)

        error_context = f"Failed in case with prefix {case['prefix']}"
        assert len(sequences) == 1, (
            f"Expected 1 sequence but found {len(sequences)}. {error_context}"
        )

        sequence = sequences[0]
        assert sequence.exists == SequenceExistence.TRUE
        assert sequence.prefix == case["prefix"], error_context
        assert sequence.first_frame == case["first_frame"], error_context
        assert sequence.last_frame == case["last_frame"], error_context
        assert sequence.extension == case["extension"], error_context
        assert sequence.delimiter == case["delimiter"], error_context
        assert sequence.suffix == case["suffix"]
        assert sequence.existing_frames == case["existing_frames"], error_context
        assert sequence.missing_frames == case["missing_frames"], error_context
        assert sequence.frame_count == case["frames_count"], error_context
        assert sequence.padding == case["padding"], error_context


def test_multiple_sequences_in_directory(parse_sequence_yaml):
    """Test finding multiple sequences in a single directory"""
    test_env_list = parse_sequence_yaml()

    # Create a directory with all test sequences
    all_files = []
    for case in test_env_list:
        all_files.extend(case["files"])

    combined_dir = Path(test_env_list[0]["tmp_dir"]) / "all_files"
    combined_dir.mkdir(exist_ok=True, parents=True)

    # Create all files in the combined directory
    for file in all_files:
        new_file = combined_dir / Path(file).name
        new_file.touch()
        assert new_file.exists(), f"Failed to create test file {new_file}"

    # Find and verify sequences
    sequences = SequenceFactory.from_directory(combined_dir)
    assert len(sequences) == len(test_env_list), (
        f"Expected {len(test_env_list)} sequences but found {len(sequences)}"
    )

    # Verify each sequence matches one of the test cases
    for sequence in sequences:
        assert sequence.exists == SequenceExistence.TRUE

        # Check that sequence properties match one of the test cases
        matching_cases = [
            case
            for case in test_env_list
            if (
                sequence.prefix == case["prefix"]
                and sequence.first_frame == case["first_frame"]
                and sequence.last_frame == case["last_frame"]
                and sequence.extension == case["extension"]
                and sequence.delimiter == case["delimiter"]
                and sequence.suffix == case["suffix"]
                and
                # sequence.suffix == case['suffix'] or (sequence.suffix is None and case['suffix'] == "") and
                sequence.existing_frames == case["existing_frames"]
                and
                # sequence.suffix == (None if case['suffix'] == "" else case['suffix']) and
                sequence.missing_frames == case["missing_frames"]
                and sequence.frame_count == case["frames_count"]
                and sequence.padding == case["padding"]
            )
        ]

        assert len(matching_cases) == 1, (
            f"Sequence {sequence.prefix} did not match exactly one test case"
        )
