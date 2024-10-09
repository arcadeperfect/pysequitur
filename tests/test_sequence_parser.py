from pysequitur import SequenceParser, Sequence

def test_find_sequences():
    # Synthetic data with various scenarios
    file_list = [
        # Basic sequences
        "render_001.exr", "render_002.exr", "render_003.exr", "render_004.exr", "render_005.exr",
        "shot_0001.jpg", "shot_0002.jpg", "shot_0003.jpg", "shot_0004.jpg", "shot_0005.jpg",
        "frame.1.png", "frame.2.png", "frame.3.png", "frame.4.png", "frame.5.png",

        # Sequences with spaces
        "scene 01.dpx", "scene 02.dpx", "scene 03.dpx", "scene 04.dpx", "scene 05.dpx",

        # Sequences without extensions
        "take_001", "take_002", "take_003", "take_004", "take_005",

        # Mixed padding
        "comp_0001.tif", "comp_002.tif", "comp_03.tif", "comp_4.tif", "comp_00005.tif",

        # Sequences with different separators
        "anim-001-v1.mov", "anim-002-v1.mov", "anim-003-v1.mov",
        "fx_001_preview.mp4", "fx_002_preview.mp4", "fx_003_preview.mp4",

        # Sequences with longer names and numbers
        "very_long_sequence_name_001.exr", "very_long_sequence_name_002.exr", "very_long_sequence_name_003.exr",
        "shot_with_high_numbers_0998.jpg", "shot_with_high_numbers_0999.jpg", "shot_with_high_numbers_1000.jpg",

        # Non-sequence files
        "not_a_sequence.txt", "random_file.doc", "another_file.pdf",

        # Sequences with similar names
        "shot_a_001.exr", "shot_a_002.exr", "shot_a_003.exr",
        "shot_ab_001.exr", "shot_ab_002.exr", "shot_ab_003.exr",

        # Sequences with special characters
        "effect@001.nk", "effect@002.nk", "effect@003.nk",
        "comp#01.psd", "comp#02.psd", "comp#03.psd",
    ]

    # Instantiate SequenceParser
    parser = SequenceParser()

    # Call find_sequences
    sequences = parser.find_sequences(file_list)

    # Expected sequences
    expected_sequences = [
        Sequence(
            name='render',
            files=[
                "render_001.exr", "render_002.exr", "render_003.exr", "render_004.exr", "render_005.exr"
            ],
            first_frame=1,
            last_frame=5,
            extension='exr'
        ),
        Sequence(
            name='shot',
            files=[
                "shot_0001.jpg", "shot_0002.jpg", "shot_0003.jpg", "shot_0004.jpg", "shot_0005.jpg"
            ],
            first_frame=1,
            last_frame=5,
            extension='jpg'
        ),
        Sequence(
            name='frame',
            files=[
                "frame.1.png", "frame.2.png", "frame.3.png", "frame.4.png", "frame.5.png"
            ],
            first_frame=1,
            last_frame=5,
            extension='png'
        ),
        Sequence(
            name='scene',
            files=[
                "scene 01.dpx", "scene 02.dpx", "scene 03.dpx", "scene 04.dpx", "scene 05.dpx"
            ],
            first_frame=1,
            last_frame=5,
            extension='dpx'
        ),
        Sequence(
            name='take',
            files=[
                "take_001", "take_002", "take_003", "take_004", "take_005"
            ],
            first_frame=1,
            last_frame=5,
            extension=''
        ),
        Sequence(
            name='comp',
            files=[
                "comp_0001.tif", "comp_00005.tif", "comp_002.tif", "comp_03.tif", "comp_4.tif"
            ],
            first_frame=1,
            last_frame=5,
            extension='tif'
        ),
        Sequence(
            name='anim',
            files=[
                "anim-001-v1.mov", "anim-002-v1.mov", "anim-003-v1.mov"
            ],
            first_frame=1,
            last_frame=3,
            extension='mov'
        ),
        Sequence(
            name='fx',
            files=[
                "fx_001_preview.mp4", "fx_002_preview.mp4", "fx_003_preview.mp4"
            ],
            first_frame=1,
            last_frame=3,
            extension='mp4'
        ),
        Sequence(
            name='very_long_sequence_name',
            files=[
                "very_long_sequence_name_001.exr", "very_long_sequence_name_002.exr", "very_long_sequence_name_003.exr"
            ],
            first_frame=1,
            last_frame=3,
            extension='exr'
        ),
        Sequence(
            name='shot_with_high_numbers',
            files=[
                "shot_with_high_numbers_0998.jpg", "shot_with_high_numbers_0999.jpg", "shot_with_high_numbers_1000.jpg"
            ],
            first_frame=998,
            last_frame=1000,
            extension='jpg'
        ),
        Sequence(
            name='shot_a',
            files=[
                "shot_a_001.exr", "shot_a_002.exr", "shot_a_003.exr"
            ],
            first_frame=1,
            last_frame=3,
            extension='exr'
        ),
        Sequence(
            name='shot_ab',
            files=[
                "shot_ab_001.exr", "shot_ab_002.exr", "shot_ab_003.exr"
            ],
            first_frame=1,
            last_frame=3,
            extension='exr'
        ),
        Sequence(
            name='effect',
            files=[
                "effect@001.nk", "effect@002.nk", "effect@003.nk"
            ],
            first_frame=1,
            last_frame=3,
            extension='nk'
        ),
        Sequence(
            name='comp',
            files=[
                "comp#01.psd", "comp#02.psd", "comp#03.psd"
            ],
            first_frame=1,
            last_frame=3,
            extension='psd'
        ),
    ]

    # Convert the list of sequences to a dictionary for easier comparison
    sequences_dict = {}
    for seq in sequences:
        key = seq.name
        if key in sequences_dict:
            # If the sequence name already exists, we need to differentiate them
            key = f"{seq.name}_{seq.extension}"
        sequences_dict[key] = seq

    expected_sequences_dict = {}
    for seq in expected_sequences:
        key = seq.name
        if key in expected_sequences_dict:
            key = f"{seq.name}_{seq.extension}"
        expected_sequences_dict[key] = seq

    # Now compare the sequences
    assert len(sequences_dict) == len(expected_sequences_dict), "Number of sequences does not match expected."

    for key, expected_seq in expected_sequences_dict.items():
        assert key in sequences_dict, f"Sequence '{key}' not found."
        actual_seq = sequences_dict[key]
        assert actual_seq.name == expected_seq.name, f"Sequence name mismatch for '{key}'."
        # Compare sorted lists of files
        assert sorted(actual_seq.files) == sorted(expected_seq.files), f"Files mismatch for sequence '{key}'."
        assert actual_seq.first_frame == expected_seq.first_frame, f"First frame mismatch for sequence '{key}'."
        assert actual_seq.last_frame == expected_seq.last_frame, f"Last frame mismatch for sequence '{key}'."
        assert actual_seq.extension == expected_seq.extension, f"Extension mismatch for sequence '{key}'."


    # Additional edge cases
    empty_file_list = []
    empty_sequences = parser.find_sequences(empty_file_list)
    assert empty_sequences == [], "Should return empty list for empty input."

    non_sequence_files = ["not_a_sequence.txt", "random_file.doc", "another_file.pdf"]
    non_sequences = parser.find_sequences(non_sequence_files)
    assert non_sequences == [], "Should return empty list when no sequences are found."

    # Test with a very long list of files (performance test)
    long_file_list = [f"long_sequence_{i:04d}.exr" for i in range(1, 10001)]
    long_sequences = parser.find_sequences(long_file_list)
    assert len(long_sequences) == 1, "Should find one sequence in long file list."
    long_seq = long_sequences[0]
    assert long_seq.name == 'long_sequence', "Sequence name mismatch in long file list."
    assert len(long_seq.files) == 10000, "Should handle very long sequences efficiently."
    assert long_seq.first_frame == 1, "First frame mismatch in long sequence."
    assert long_seq.last_frame == 10000, "Last frame mismatch in long sequence."
    assert long_seq.extension == 'exr', "Extension mismatch in long sequence."

if __name__ == "__main__":
    pytest.main([__file__])
