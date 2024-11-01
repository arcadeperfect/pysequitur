from pathlib import Path
from pysequitur.file_sequence import Item, Parser, Renamer
import os


def test_file_sequence_operations(create_files_from_list):
    print("\n----  test_file_sequence_operations ----\n")
    
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
    assert all(item.name == "sequence" for item in sequence.items)
    assert sequence.name == "sequence"
    
    # Test rename with string
    sequence.rename("renamed")
    assert all(item.exists for item in sequence.items)
    assert all(item.name == "renamed" for item in sequence.items)
    assert sequence.name == "renamed"
    
    # Test rename with Renamer object
    renamer = Renamer(
        name="complex",
        separator=".",
        padding=5,
        post_numeral="_v1",
        extension="exr"
    )
    sequence.rename(renamer)
    
    # Verify all items were renamed correctly
    for item in sequence.items:
        assert item.exists
        assert item.name == "complex"
        assert item.separator == "."
        assert item.padding == 5
        assert item.post_numeral == "_v1"
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
    
    print("\n---- test_file_sequence_errors ----\n")
    
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
    
    print("\n----  test_file_sequence_complex ----\n")
    
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
    assert sequence.name == "comp@#$"
    assert sequence.post_numeral == "_post"
    
    
    # Test renaming complex sequence
    renamer = Renamer(name="new@#$", post_numeral="_final")
    sequence.rename(renamer)
    
    
    # Verify all items were renamed correctly
    for item in sequence.items:
        assert item.exists
        assert item.name == "new@#$"
        assert item.post_numeral == "_final"
    
    # Clean up
    sequence.delete()
    assert all(not item.exists for item in sequence.items)
    
    print("\n----  test_file_sequence_operations complete ----\n")