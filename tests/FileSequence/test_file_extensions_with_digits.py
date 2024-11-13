from pysequitur import FileSequence, Item, Components

def test_file_extensions_with_digits():
    
    
    file = "file.0001.ex1" # i dunno it could happen
    
    item = Item.from_file_name(file)

    assert isinstance(item, Item)
    assert item.prefix == "file"
    assert item.delimiter == "."
    assert item.frame_string == "0001"
    assert item.extension == "ex1"
    
    
    components = Components(prefix="file", delimiter=".", padding=4, suffix="suffix", extension="ex1")
    
    item = Item.from_components(components, 1)
    
    assert isinstance(item, Item)
    assert item.prefix == "file"
    assert item.delimiter == "."
    assert item.frame_string == "0001"
    assert item.suffix == "suffix"
    assert item.extension == "ex1"
    
    files = ["file.1001_suffix.123",
        "file.1002_suffix.123",
        "file.1003_suffix.123",
        "file.1004_suffix.123",
        "file.1005_suffix.123",]
    
    sequence = FileSequence.find_sequences_in_filename_list(files)[0]
    
    assert isinstance(sequence, FileSequence)
    assert sequence.prefix == "file"
    assert sequence.delimiter == "."
    assert sequence.padding == 4
    assert sequence.suffix == "_suffix"
    assert sequence.extension == "123"
    assert sequence.frame_count == 5