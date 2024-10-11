# from pysequitur import SequenceParser


# def test_parse_filename():
#     parser = SequenceParser()

#     test_cases = [
#         # Filenames with same name but different extensions
#         ("sequence_001.exr", {'name': 'sequence', 'separator': '_', 'frame': '001', 'ext': 'exr'}),
#         ("sequence_001.jpg", {'name': 'sequence', 'separator': '_', 'frame': '001', 'ext': 'jpg'}),
#         ("sequence_001.png", {'name': 'sequence', 'separator': '_', 'frame': '001', 'ext': 'png'}),
        
#         # Filenames with different separators
#         ("sequence-001.exr", {'name': 'sequence', 'separator': '-', 'frame': '001', 'ext': 'exr'}),
#         ("sequence.001.exr", {'name': 'sequence', 'separator': '.', 'frame': '001', 'ext': 'exr'}),
        
#         # Filenames with special characters in name
#         ("sequence@001.exr", {'name': 'sequence', 'separator': '@', 'frame': '001', 'ext': 'exr'}),
#         ("sequence#001.exr", {'name': 'sequence', 'separator': '#', 'frame': '001', 'ext': 'exr'}),
        
#         # Filenames without extension
#         ("sequence_001", {'name': 'sequence', 'separator': '_', 'frame': '001', 'ext': None}),
        
#         # Filenames without separator
#         ("sequence001.exr", {'name': 'sequence', 'separator': '', 'frame': '001', 'ext': 'exr'}),
        
#         # Filenames with multiple dots
#         ("sequence.v1.001.exr", {'name': 'sequence.v1', 'separator': '.', 'frame': '001', 'ext': 'exr'}),
        
#         # Filenames with varying frame number lengths
#         ("sequence_1.exr", {'name': 'sequence', 'separator': '_', 'frame': '1', 'ext': 'exr'}),
#         ("sequence_000001.exr", {'name': 'sequence', 'separator': '_', 'frame': '000001', 'ext': 'exr'}),
        
#         # Filenames with letters in frame number (should not match)
#         ("sequence_00a1.exr", None),
        
#         # Filenames with no frame number (should not match)
#         ("sequence_.exr", None),
        
#         # Filenames with leading/trailing spaces
#         (" sequence_001.exr", {'name': ' sequence', 'separator': '_', 'frame': '001', 'ext': 'exr'}),
#         ("sequence_001.exr ", {'name': 'sequence', 'separator': '_', 'frame': '001', 'ext': 'exr'}),
        
#         # Filenames with non-matching patterns
#         ("random_file.txt", None),
#         ("another_sequence.exr", None),
#     ]

#     for filename, expected in test_cases:
#         result = parser.parse_filename(filename)
#         if expected is None:
#             assert result is None, f"Expected None for filename '{filename}', got {result}"
#         else:
#             # Adjust None to match the actual output (None vs. empty string for 'ext')
#             expected_ext = expected['ext'] if expected['ext'] is not None else None
#             result_ext = result['ext'] if result['ext'] else None

#             assert result is not None, f"Expected a match for filename '{filename}', got None"
#             assert result['name'] == expected['name'], f"Name mismatch for '{filename}'"
#             assert result['separator'] == expected['separator'], f"Separator mismatch for '{filename}'"
#             assert result['frame'] == expected['frame'], f"Frame mismatch for '{filename}'"
#             assert result_ext == expected_ext, f"Extension mismatch for '{filename}'"

# if __name__ == "__main__":
#     pytest.main([__file__])
