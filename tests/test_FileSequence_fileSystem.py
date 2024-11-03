from pathlib import Path
from pysequitur.file_sequence import Item, Parser, Renamer
import os
import cProfile
import random

def test_file_sequence_operations(create_files_from_list):
    

    # Basic sequence of files
    files = [
        'sequence_0001.png',
        'sequence_0002.png',
        'sequence_0003.png',
        'sequence_0004.png'
    ]
    
    paths = create_files_from_list(files)
    directory = paths[0].parent
    new_directory = directory / "moved_sequences"
    os.mkdir(new_directory)
    
    # Get the sequence
    sequences = Parser.find_sequences(files, directory)
    assert len(sequences) == 1
    sequence = sequences[0]
    
    # Verify initial state
    assert len(sequence.items) == 4
    assert all(item.exists for item in sequence.items)
    assert all(item.prefix == "sequence" for item in sequence.items)
    assert sequence.prefix == "sequence"
    
    # Test rename with string
    sequence.rename("renamed")
    assert all(item.exists for item in sequence.items)
    assert all(item.prefix == "renamed" for item in sequence.items)
    assert sequence.prefix == "renamed"
    
    # Test rename with Renamer object
    renamer = Renamer(
        prefix="complex",
        delimiter=".",
        padding=5,
        suffix="_v1",
        extension="exr"
    )
    sequence.rename(renamer)
    
    # Verify all items were renamed correctly
    for item in sequence.items:
        assert item.exists
        assert item.prefix == "complex"
        assert item.delimiter == "."
        assert item.padding == 5
        assert item.suffix == "_v1"
        assert item.extension == "exr"
    
    # Test move operation
    sequence.move(new_directory)
    assert all(item.exists for item in sequence.items)
    assert all(str(item.directory) == str(new_directory) for item in sequence.items)
    
    # Test delete operation
    sequence.delete()
    assert all(not item.exists for item in sequence.items)
    
    # Clean up
    os.rmdir(new_directory)
    
    
    # Test error handling with mixed sequences
    mixed_files = [
        'mixed_0001.png',
        'mixed_0002.png',
        'different_0003.png',  # Different name
        'different_0004.png',  # Different name
        'mixed.0004.png'       # Different separator
    ]
    
    paths = create_files_from_list(mixed_files)
    sequences = Parser.find_sequences(mixed_files, directory)
    
    # Should create two sequences due to different names
    assert len(sequences) >= 2
    
    # Clean up test files
    for path in paths:
        path.unlink()
    
    
    # Test with complex sequence including special characters and post numerals
    complex_files = [
        'comp@#$_0001_post.exr',
        'comp@#$_0002_post.exr',
        'comp@#$_0003_post.exr'
    ]
    
    paths = create_files_from_list(complex_files)
    for path in paths:
        assert path.exists()
    sequences = Parser.find_sequences(paths)
    assert len(sequences) == 1
    sequence = sequences[0]
    assert sequence.items[0].exists
    # Verify initial state
    assert sequence.prefix == "comp@#$"
    assert sequence.suffix == "_post"
    
    
    # Test renaming complex sequence
    renamer = Renamer(prefix="new@#$", suffix="_final")
    sequence.rename(renamer)
    
    
    # Verify all items were renamed correctly
    for item in sequence.items:
        assert item.exists
        assert item.prefix == "new@#$"
        assert item.suffix == "_final"
    
    # Clean up
    sequence.delete()
    assert all(not item.exists for item in sequence.items)
    



    #long file list with missing file

    for i in range(1):

        file_count = 1000
        missing_files = 50

        files = [f"img_{i:04d}.png" for i in range(file_count)]


    
        random.seed(i)
        last_index = len(files) - 1
        indices_to_remove = random.sample(range(1, len(files) - 1), missing_files)
        files = [item for i, item in enumerate(files) if i not in indices_to_remove]


        paths = create_files_from_list(files)
        for path in paths:
            assert path.exists()

        sequences = Parser.find_sequences(paths)
        s = sequences[0]
        s.rename("renamed")
        
        paths = create_files_from_list(complex_files)
        assert len(sequences) == 1
        sequence = sequences[0]

        assert len(sequence.missing_frames) == missing_files

        sequence.rename("renamed")
        sequence._validate()
        sequence.delete()



    # Test copying a sequence
    copy_files = [
        'copy_0001.png',
        'copy_0002.png',
        'copy_0003.png',
        'copy_0004.png'
    ]

    paths = create_files_from_list(copy_files)
    directory = paths[0].parent
    copy_directory = directory / "copied_sequences"
    os.mkdir(copy_directory)

    # Get the sequence
    sequences = Parser.find_sequences(copy_files, directory)
    assert len(sequences) == 1
    sequence = sequences[0]

    # Copy the sequence with a new name
    new_name = "copied_sequence"
    copied_sequence = sequence.copy(new_name)

    # Verify the copied sequence
    assert len(copied_sequence.items) == len(sequence.items)
    assert copied_sequence.prefix == new_name
    assert all(item.exists for item in copied_sequence.items)
    assert all(item.prefix == new_name for item in copied_sequence.items)

    # Copy the sequence with a new name and directory
    new_directory_name = "new_directory"
    new_directory = copy_directory / new_directory_name
    os.mkdir(new_directory)
    copied_sequence_with_dir = sequence.copy(new_name, new_directory)

    # Verify the copied sequence with new directory
    assert len(copied_sequence_with_dir.items) == len(sequence.items)
    assert copied_sequence_with_dir.prefix == new_name
    assert all(item.exists for item in copied_sequence_with_dir.items)
    assert all(item.prefix == new_name for item in copied_sequence_with_dir.items)
    assert all(str(item.directory) == str(new_directory) for item in copied_sequence_with_dir.items)

    # Clean up
    for item in copied_sequence.items:
        item.delete()
    for item in copied_sequence_with_dir.items:
        item.delete()
    os.rmdir(copy_directory / new_directory_name)
    os.rmdir(copy_directory)