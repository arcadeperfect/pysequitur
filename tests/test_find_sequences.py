# from pysequitur import find_sequences, list_sequence_files, Sequence


# def test_find_sequences():
#     # Synthetic data with various scenarios
#     file_list = [
#         # Basic sequences
#         "render_001.exr", "render_002.exr", "render_003.exr", "render_004.exr", "render_005.exr",
#         "shot_0001.jpg", "shot_0002.jpg", "shot_0003.jpg", "shot_0004.jpg", "shot_0005.jpg",
#         "frame.1.png", "frame.2.png", "frame.3.png", "frame.4.png", "frame.5.png",

#         # Sequences with spaces
#         "scene 01.dpx", "scene 02.dpx", "scene 03.dpx", "scene 04.dpx", "scene 05.dpx",

#         # Sequences without extensions
#         "take_001", "take_002", "take_003", "take_004", "take_005",

#         # Mixed padding and special characters
#         "comp_0001.tif", "comp_002.tif", "comp_03.tif", "comp_4.tif", "comp_00005.tif",
#         "comp#01.psd", "comp#02.psd", "comp#03.psd",

#         # Sequences with different separators
#         "anim-001-v1.mov", "anim-002-v1.mov", "anim-003-v1.mov",
#         "fx_001_preview.mp4", "fx_002_preview.mp4", "fx_003_preview.mp4",

#         # Sequences with longer names and numbers
#         "very_long_sequence_name_001.exr", "very_long_sequence_name_002.exr", "very_long_sequence_name_003.exr",
#         "shot_with_high_numbers_0998.jpg", "shot_with_high_numbers_0999.jpg", "shot_with_high_numbers_1000.jpg",

#         # Non-sequence files
#         "not_a_sequence.txt", "random_file.doc", "another_file.pdf",

#         # Sequences with similar names
#         "shot_a_001.exr", "shot_a_002.exr", "shot_a_003.exr",
#         "shot_ab_001.exr", "shot_ab_002.exr", "shot_ab_003.exr",

#         # Sequences with special characters
#         "effect@001.nk", "effect@002.nk", "effect@003.nk",
#     ]

#     # Expected sequences as list of Sequence instances
#     expected_sequences = [
#         Sequence(
#             name='anim',
#             files=['anim-001-v1.mov', 'anim-002-v1.mov', 'anim-003-v1.mov'],
#             first_frame=1,
#             last_frame=3,
#             extension='mov'
#         ),
#         Sequence(
#             name='comp',
#             files=['comp#01.psd', 'comp#02.psd', 'comp#03.psd'],
#             first_frame=1,
#             last_frame=3,
#             extension='psd'
#         ),
#         Sequence(
#             name='comp',
#             files=['comp_0001.tif', 'comp_00005.tif', 'comp_002.tif', 'comp_03.tif', 'comp_4.tif'],
#             first_frame=1,
#             last_frame=5,
#             extension='tif'
#         ),
#         Sequence(
#             name='effect',
#             files=['effect@001.nk', 'effect@002.nk', 'effect@003.nk'],
#             first_frame=1,
#             last_frame=3,
#             extension='nk'
#         ),
#         Sequence(
#             name='frame',
#             files=['frame.1.png', 'frame.2.png', 'frame.3.png', 'frame.4.png', 'frame.5.png'],
#             first_frame=1,
#             last_frame=5,
#             extension='png'
#         ),
#         Sequence(
#             name='fx',
#             files=['fx_001_preview.mp4', 'fx_002_preview.mp4', 'fx_003_preview.mp4'],
#             first_frame=1,
#             last_frame=3,
#             extension='mp4'
#         ),
#         Sequence(
#             name='render',
#             files=['render_001.exr', 'render_002.exr', 'render_003.exr', 'render_004.exr', 'render_005.exr'],
#             first_frame=1,
#             last_frame=5,
#             extension='exr'
#         ),
#         Sequence(
#             name='scene',
#             files=['scene 01.dpx', 'scene 02.dpx', 'scene 03.dpx', 'scene 04.dpx', 'scene 05.dpx'],
#             first_frame=1,
#             last_frame=5,
#             extension='dpx'
#         ),
#         Sequence(
#             name='shot',
#             files=['shot_0001.jpg', 'shot_0002.jpg', 'shot_0003.jpg', 'shot_0004.jpg', 'shot_0005.jpg'],
#             first_frame=1,
#             last_frame=5,
#             extension='jpg'
#         ),
#         Sequence(
#             name='shot_a',
#             files=['shot_a_001.exr', 'shot_a_002.exr', 'shot_a_003.exr'],
#             first_frame=1,
#             last_frame=3,
#             extension='exr'
#         ),
#         Sequence(
#             name='shot_ab',
#             files=['shot_ab_001.exr', 'shot_ab_002.exr', 'shot_ab_003.exr'],
#             first_frame=1,
#             last_frame=3,
#             extension='exr'
#         ),
#         Sequence(
#             name='shot_with_high_numbers',
#             files=['shot_with_high_numbers_0998.jpg', 'shot_with_high_numbers_0999.jpg', 'shot_with_high_numbers_1000.jpg'],
#             first_frame=998,
#             last_frame=1000,
#             extension='jpg'
#         ),
#         Sequence(
#             name='take',
#             files=['take_001', 'take_002', 'take_003', 'take_004', 'take_005'],
#             first_frame=1,
#             last_frame=5,
#             extension=''
#         ),
#         Sequence(
#             name='very_long_sequence_name',
#             files=['very_long_sequence_name_001.exr', 'very_long_sequence_name_002.exr', 'very_long_sequence_name_003.exr'],
#             first_frame=1,
#             last_frame=3,
#             extension='exr'
#         ),
#     ]

#     # Find sequences
#     sequences = find_sequences(file_list)

#     # Sort sequences by name and extension for comparison
#     sequences.sort(key=lambda s: (s.name, s.extension))
#     expected_sequences.sort(key=lambda s: (s.name, s.extension))

#     # Compare sequences
#     for seq, expected_seq in zip(sequences, expected_sequences):
#         assert seq.name == expected_seq.name, f"Sequence name mismatch: {seq.name} != {expected_seq.name}"
#         assert sorted(seq.files) == sorted(expected_seq.files), f"Files mismatch in sequence '{seq.name}'"
#         assert seq.first_frame == expected_seq.first_frame, f"First frame mismatch in sequence '{seq.name}'"
#         assert seq.last_frame == expected_seq.last_frame, f"Last frame mismatch in sequence '{seq.name}'"
#         assert seq.extension == expected_seq.extension, f"Extension mismatch in sequence '{seq.name}'"

#     # Check for any unexpected sequences
#     assert len(sequences) == len(expected_sequences), (
#         f"Number of sequences mismatch: found {len(sequences)}, expected {len(expected_sequences)}"
#     )

#     # Optionally, print the sequences
#     for seq in sequences:
#         print(f"Sequence Name: {seq.name}")
#         print(f"Files: {seq.files}")
#         print(f"First Frame: {seq.first_frame}")
#         print(f"Last Frame: {seq.last_frame}")
#         print(f"Extension: {seq.extension}")
#         print()