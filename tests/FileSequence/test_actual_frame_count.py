from pysequitur import FileSequence, Components

def test_actual_frame_count():
    
    files = [
        "file.0001.exr",
        "file.0002.exr",
        "file.0003.exr",
        "file.0004.exr",
    ]
    
    sequences = FileSequence.find_sequences_in_filename_list(files)    
    assert len(sequences) == 1
    sequence = sequences[0]
    
    assert sequence.actual_frame_count == 4
    assert sequence.frame_count == 4

    files = [
        "file.0001.exr",
        "file.0002.exr",

        "file.0004.exr",
    ]
    
    sequences = FileSequence.find_sequences_in_filename_list(files)    
    assert len(sequences) == 1
    sequence = sequences[0]
  
    assert sequence.frame_count == 4
    assert sequence.actual_frame_count == 3