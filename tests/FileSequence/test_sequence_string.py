from pysequitur.file_sequence import FileSequence, SequenceFactory
from pathlib import Path


def test_sequence_string():
    print("\n")
    # Create test directory and files
    test_dir = Path("test_sequence")
    test_dir.mkdir(exist_ok=True)

    print(test_dir.absolute())

    assert test_dir.exists()
    print(test_dir.exists())

    # Test cases with different patterns
    test_cases = [
        {
            "files": ["render.0001.exr", "render.0002.exr", "render.0003.exr"],
            "expected": "render.####.exr",
        },
        {
            "files": ["shot_001_v.exr", "shot_002_v.exr", "shot_003_v.exr"],
            "expected": "shot_###_v.exr",
        },
        {
            "files": [
                "comp-0001-preview.exr",
                "comp-0002-preview.exr",
                "comp-0003-preview.exr",
            ],
            "expected": "comp-####-preview.exr",
        },
        {
            "files": [
                "anim.00001.beauty.exr",
                "anim.00002.beauty.exr",
                "anim.00003.beauty.exr",
            ],
            "expected": "anim.#####.beauty.exr",
        },
    ]

    for case in test_cases:
        # Create files
        for file in case["files"]:
            (test_dir / file).touch()
            assert (test_dir / file).exists()
            print((test_dir / file).exists())

        # Get sequence
        sequences = SequenceFactory.from_directory(test_dir)
        print(f"found: {len(sequences)}")
        sequence = sequences[0]

        # Test sequence string
        assert sequence.sequence_string == case["expected"]

        # Cleanup files
        for file in case["files"]:
            (test_dir / file).unlink()

    # Clean up directory
    test_dir.rmdir()
    assert not test_dir.exists()
    print(test_dir.exists())
