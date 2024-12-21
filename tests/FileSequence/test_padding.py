from pysequitur import FileSequence



def test_padding():

    
    data = {
        4:
        [
         "file.997.exr",
         "file.998.exr",
         "file.999.exr",
         "file.1000.exr",
        ],
        4:[
         "file.1001.exr",
         "file.1002.exr",
         "file.1003.exr",
         "file.1004.exr",
        ],
        5:[
         "file.10001.exr",
         "file.10002.exr",
         "file.10003.exr",
         "file.10004.exr",
        ],
    }

    for expected, files in data.items():
        sequence = FileSequence.find_sequences_in_filename_list(files)
        assert len(sequence) == 1
        assert sequence[0].padding == expected
         
    