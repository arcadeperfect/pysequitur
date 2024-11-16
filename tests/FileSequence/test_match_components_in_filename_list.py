from pysequitur import FileSequence, Components

def test_match_components_in_filename_list():

    files = [
        "file.0001.exr",
        "file.0002.exr",
        "file.0003.exr",

        "file.001.exr",
        "file.002.exr",
        "file.003.exr",
        "file.004.exr",
        "file.005.exr",

        "file.0001.jpg",
        "file.0002.jpg",
        "file.0003.jpg",
        "file.0004.jpg",
        "file.0005.jpg",

        "file.0001_suffix.exr",
        "file.0002_suffix.exr",
        "file.0003_suffix.exr",
        "file.0004_suffix.exr",
        "file.0005_suffix.exr",
        "file.0006_suffix.exr",

        "another_file.0001.exr",
        "another_file.0002.exr",
        "another_file.0003.exr",
        "another_file.0004.exr",
        "another_file.0005.exr",
        "another_file.0006.exr",
        "another_file.0007.exr",

        "another_file.0001_suffix.jpg",
        "another_file.0002_suffix.jpg",
        "another_file.0003_suffix.jpg",
        "another_file.0004_suffix.jpg",
        "another_file.0005_suffix.jpg",
        "another_file.0006_suffix.jpg",
        "another_file.0007_suffix.jpg",
        "another_file.0008_suffix.jpg",
        
        "another_file_00001.jpg",
        "another_file_00002.jpg",
        "another_file_00003.jpg",
        "another_file_00004.jpg",
        "another_file_00005.jpg",
        "another_file_00006.jpg",
        "another_file_00007.jpg",
        "another_file_00008.jpg",
        "another_file_00009.jpg",

    ]

    print("\n")

    components = Components(prefix="file")
    sequences = FileSequence.match_components_in_filename_list(components, files)
    assert len(sequences) == 4

    components = Components(suffix="_suffix")
    sequences = FileSequence.match_components_in_filename_list(components, files)
    assert len(sequences) == 2

    components = Components(prefix = "file", suffix="_suffix")
    sequences = FileSequence.match_components_in_filename_list(components, files)
    assert len(sequences) == 1

    components = Components(extension = "exr")
    sequences = FileSequence.match_components_in_filename_list(components, files)
    assert len(sequences) == 4
    
    components = Components(padding = 4)
    sequences = FileSequence.match_components_in_filename_list(components, files)
    assert len(sequences) == 5
    
    components = Components(padding = 4, extension = "exr", suffix = "")
    sequences = FileSequence.match_components_in_filename_list(components, files)
    assert len(sequences) == 2
    
    components = Components(prefix = "another_file", delimiter= "_")
    sequences = FileSequence.match_components_in_filename_list(components, files)
    assert len(sequences) == 1