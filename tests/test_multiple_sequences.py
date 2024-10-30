from pysequitur.file_sequence import FileSequence, Parser
from pathlib import Path
import pytest

def normalize_empty(value):
    return None if value == '' else value

def compare(actual, expected):
    assert normalize_empty(actual) == normalize_empty(expected)

# def test_multiple_sequences(load_test_cases):
#     print("\n ----- Testing Multiple Sequences -----")

#     test_cases_dir = Path(__file__).parent / 'FileSequence_test_cases'
#     yaml_file = test_cases_dir / '2.yaml'

#     cases = load_test_cases(yaml_file)

#     random_files = [
#     "project_notes_final.txt",
#     "DSC4587.jpg",
#     "meeting_2024_v2.doc",
#     "backup_old.zip",
#     "reference-image!.png",
#     "script_draft_final_FINAL.pdf",
#     "temp~1.tmp",
#     "screenshot_2024-03-15.png",
#     "my.personal.notes.md",
#     "asset_library_ref#2.blend"
#     ]



#     for case in cases:
#         all_files = []
        

#         sequences = case['sequences']
        
#         # Collect all files and build a lookup dictionary
#         sequence_data = {}  # Will store our sequence configs by name
#         for sequence in sequences:
#             for seq_name, seq_value in sequence.items():
#                 sequence_data[seq_name] = seq_value  # Store config by name
#                 all_files.extend(seq_value['files'])

#         all_files.extend(random_files)

#         fileSequences = Parser.find_sequences(all_files)

#         # Match and test each parsed sequence
#         for fileSequence in fileSequences:
#             # Try to find matching sequence in our YAML data
#             sequence_name = fileSequence.name
            
#             # Debug print to see what we're matching
#             print(f"Looking for match for: {sequence_name}")
#             print(f"Available sequences: {list(sequence_data.keys())}")
            
#             # Find the matching sequence data
#             if sequence_name in sequence_data:
#                 yaml_seq = sequence_data[sequence_name]
                
#                 # Now compare all the attributes
#                 compare(fileSequence.first_frame, yaml_seq['first_frame'])
#                 compare(fileSequence.last_frame, yaml_seq['last_frame'])
#                 compare(fileSequence.extension, yaml_seq['extension'])
#                 compare(fileSequence.separator, yaml_seq['separator'])
#                 compare(fileSequence.post_numeral, yaml_seq['post_numeral'])
#                 compare(fileSequence.existing_frames, yaml_seq['existing_frames'])
#                 compare(list(fileSequence.missing_frames), yaml_seq['missing_frames'])
#                 compare(fileSequence.frame_count, yaml_seq['frames_count'])
#                 compare(fileSequence.padding, yaml_seq['padding'])
#             else:
#                 pytest.fail(f"No matching sequence found for {sequence_name}")


def test_multiple_sequences(load_test_cases):
    print("\n ----- Testing Multiple Sequences -----")

    test_cases_dir = Path(__file__).parent / 'FileSequence_test_cases'
    yaml_file = test_cases_dir / '2.yaml'

    cases = load_test_cases(yaml_file)

    random_files = [
        "project_notes_final.txt",
        "DSC4587.jpg",
        "meeting_2024_v2.doc",
        "backup_old.zip",
        "reference-image!.png",
        "script_draft_final_FINAL.pdf",
        "temp~1.tmp",
        "screenshot_2024-03-15.png",
        "my.personal.notes.md",
        "asset_library_ref#2.blend"
    ]

    for case_index, case in enumerate(cases):
        print(f"\nTesting case {case_index + 1}: {case['description']}")
        all_files = []

        sequences = case['sequences']
        
        # Collect all files and build a lookup dictionary
        sequence_data = {}  # Will store our sequence configs by name
        for sequence in sequences:
            for seq_name, seq_value in sequence.items():
                sequence_data[seq_name] = seq_value  # Store config by name
                all_files.extend(seq_value['files'])

        all_files.extend(random_files)

        fileSequences = Parser.find_sequences(all_files)

        # Match and test each parsed sequence
        for fileSequence in fileSequences:
            sequence_name = fileSequence.name
            
            print(f"\nTesting sequence: {sequence_name}")
            
            if sequence_name in sequence_data:
                yaml_seq = sequence_data[sequence_name]
                
                # Store all comparisons to report them together
                differences = []
                
                # Compare all attributes and collect differences
                attributes_to_check = [
                    ('first_frame', fileSequence.first_frame, yaml_seq['first_frame']),
                    ('last_frame', fileSequence.last_frame, yaml_seq['last_frame']),
                    ('extension', fileSequence.extension, yaml_seq['extension']),
                    ('separator', fileSequence.separator, yaml_seq['separator']),
                    ('post_numeral', fileSequence.post_numeral, yaml_seq['post_numeral']),
                    ('existing_frames', fileSequence.existing_frames, yaml_seq['existing_frames']),
                    ('missing_frames', list(fileSequence.missing_frames), yaml_seq['missing_frames']),
                    ('frame_count', fileSequence.frame_count, yaml_seq['frames_count']),
                    ('padding', fileSequence.padding, yaml_seq['padding'])
                ]

                for attr_name, actual, expected in attributes_to_check:
                    try:
                        compare(actual, expected)
                    except AssertionError:
                        differences.append(f"  {attr_name}: expected {expected}, got {actual}")

                # If we found any differences, raise a detailed error
                if differences:
                    error_msg = f"\nFailure in case {case_index + 1}: {case['description']}\n"
                    error_msg += f"Sequence: {sequence_name}\n"
                    error_msg += "Files in sequence:\n"
                    error_msg += "\n".join(f"  {f}" for f in yaml_seq['files'])
                    error_msg += "\nDifferences found:\n"
                    error_msg += "\n".join(differences)
                    pytest.fail(error_msg)

            else:
                pytest.fail(f"No matching sequence found for {sequence_name} in case {case_index + 1}: {case['description']}")