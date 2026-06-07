from pysequitur import ItemParser

def test_padding_converter():

    data = [
        ("file.#####.exr",
        "file.#####.exr"),
        ("file.####.exr",
        "file.####.exr"),
        ("file.%04d.exr",
        "file.####.exr"),
        ("file.%05d.exr",
        "file.#####.exr")
    ]

    for case in data:
        
        converted = ItemParser.convert_padding_to_hashes(case[0])
        assert converted == case[1]

    