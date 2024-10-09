from pysequitur import find_sequences, list_sequence_files

def test_list_sequence_files():
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

    # Test cases
    test_cases = [
        ("render", "exr", ["render_001.exr", "render_002.exr", "render_003.exr", "render_004.exr", "render_005.exr"]),
        ("shot", "jpg", ["shot_0001.jpg", "shot_0002.jpg", "shot_0003.jpg", "shot_0004.jpg", "shot_0005.jpg"]),
        ("frame", "png", ["frame.1.png", "frame.2.png", "frame.3.png", "frame.4.png", "frame.5.png"]),
        ("scene", "dpx", ["scene 01.dpx", "scene 02.dpx", "scene 03.dpx", "scene 04.dpx", "scene 05.dpx"]),
        ("take", "", ["take_001", "take_002", "take_003", "take_004", "take_005"]),
        ("comp", "tif", ["comp_0001.tif", "comp_002.tif", "comp_03.tif", "comp_4.tif", "comp_00005.tif"]),
        ("anim-", "mov", ["anim-001-v1.mov", "anim-002-v1.mov", "anim-003-v1.mov"]),
        ("fx", "mp4", ["fx_001_preview.mp4", "fx_002_preview.mp4", "fx_003_preview.mp4"]),
        ("very_long_sequence_name", "exr", ["very_long_sequence_name_001.exr", "very_long_sequence_name_002.exr", "very_long_sequence_name_003.exr"]),
        ("shot_with_high_numbers", "jpg", ["shot_with_high_numbers_0998.jpg", "shot_with_high_numbers_0999.jpg", "shot_with_high_numbers_1000.jpg"]),
        ("non_existent", "exr", []),
        ("shot_a", "exr", ["shot_a_001.exr", "shot_a_002.exr", "shot_a_003.exr"]),
        ("shot_ab", "exr", ["shot_ab_001.exr", "shot_ab_002.exr", "shot_ab_003.exr"]),
        ("effect@", "nk", ["effect@001.nk", "effect@002.nk", "effect@003.nk"]),
        ("comp#", "psd", ["comp#01.psd", "comp#02.psd", "comp#03.psd"]),
    ]

    for sequence_name, extension, expected_result in test_cases:
        result = list_sequence_files(file_list, sequence_name, extension)
        assert result == expected_result, f"Failed for sequence '{sequence_name}' with extension '{extension}'"

    # Additional edge cases
    assert list_sequence_files([], "any", "ext") == [], "Should return empty list for empty input"
    assert list_sequence_files(file_list, "not_a_sequence", "txt") == [], "Should return empty list for non-sequence file"
    assert list_sequence_files(file_list, "random", "doc") == [], "Should return empty list for non-existent sequence"

    # Test with a very long list of files (performance test)
    long_file_list = [f"long_sequence_{i:04d}.exr" for i in range(1, 10001)]
    long_result = list_sequence_files(long_file_list, "long_sequence", "exr")
    assert len(long_result) == 10000, "Should handle very long sequences efficiently"

if __name__ == "__main__":
    pytest.main([__file__])
