from pysequitur import FileSequence


def test_FileSequence():

    sequence1 = FileSequence("name", ["file1", "file2"], 1, 5, "exr")
    assert sequence1.name == "name"
    assert sequence1.files == ["file1", "file2"]
    assert sequence1.first_frame == 1
    assert sequence1.last_frame == 5
    assert sequence1.extension == "exr"

    sequence2 = FileSequence("name", ["file1", "file2"], 1, 5, "exr")
  
    sequence3 = FileSequence("name2", ["file1", "file2"], 1, 5, "exr")

    assert sequence1 == sequence2
    assert sequence1 != sequence3
    
    
    