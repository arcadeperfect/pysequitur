from pysequitur import FileSequence, SequenceParser, Item
from pathlib import Path

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


if __name__ == "__main__":


    path = Path("/a/b/c")
    file = "render_001_moist"

    item = FileSequence._parse_filename(file, path )


    print(item.path)