from pysequitur import FileSequence, Components


def test_existing_missing_frames():
    
    files = [
        "file.0001.exr",
        "file.0002.exr",
        "file.0003.exr",
        "file.0004.exr",
        "file.0005.exr",
    ]
    
    sequence = FileSequence.find_sequences_in_filename_list(files)[0]
    assert sequence.frame_count == 5
    assert sequence.actual_frame_count == 5
    assert sequence.missing_frames == []
    
    files = [
        "file.0001.exr",
        "file.0002.exr",
        
        "file.0004.exr",
        "file.0005.exr",
    ]
    
    sequence = FileSequence.find_sequences_in_filename_list(files)[0]
    assert sequence.frame_count == 5
    assert sequence.actual_frame_count == 4
    assert sequence.missing_frames == [3]
    
    files = [
        "file.0001.exr",
        "file.0002.exr",
        
        "file.0004.exr",
        "file.0005.exr",
        
        "file.0007.exr",
    ]
    
    sequence = FileSequence.find_sequences_in_filename_list(files)[0]
    assert sequence.frame_count == 7
    assert sequence.actual_frame_count == 5
    assert sequence.missing_frames == [3,6]