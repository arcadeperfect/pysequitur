from pysequitur.file_sequence import SequenceParser


def test_allowed_extensions(parse_sequence_yaml):
    data = [
        "file_001.exr",
        "file_002.exr",
        "file_003.exr",
        "file_004.exr",
        "single_frame.1000.dpx",
        "rogue_A.jpg",
        "rogue_B.tif",
        "invalid.exe",
    ]

    allowed_extensions = ["exr", "dpx", "jpg", "tif"]

    results = SequenceParser.from_file_list(
        data, 1, allowed_extensions=allowed_extensions
    )

    assert len(results.rogues) == 2

    data = [
        "file_001.exr",
        "file_002.exr",
        "file_003.exr",
        "file_004.exr",
        "single_frame.1000.dpx",
        "rogue_A.jpg",
        "rogue_B.tif",
        "invalid.exe",
    ]

    allowed_extensions = ["exr", "dpx", "jpg", "tif"]

    results = SequenceParser.from_file_list(
        data, 2, allowed_extensions=allowed_extensions
    )

    assert len(results.rogues) == 2

    data = [
        "file_001.exr",
        "file_002.exr",
        "file_003.exr",
        "file_004.exr",
        "single_frame.1000.dpx",
        "rogue_A.jpg",
        "rogue_B.tif",
        "invalid.exe",
    ]

    allowed_extensions = ["exr", "dpx", "jpg"]

    results = SequenceParser.from_file_list(
        data, 2, allowed_extensions=allowed_extensions
    )

    assert len(results.rogues) == 1
