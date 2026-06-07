from pysequitur.file_sequence import FileSequence, SequenceExistence, SequenceFactory
from pathlib import Path
import shutil
import os


def test_exists():
    # Create test directory and files
    test_dir = Path("test_sequence")
    test_dir.mkdir(exist_ok=True)

    files = [
        "file.0001.exr",
        "file.0002.exr",
        "file.0003.exr",
        "file.0004.exr",
        "file.0005.exr",
        "file.0006.exr",
    ]

    # Create the test files
    for file in files:
        (test_dir / file).touch()

    # Find sequences in directory
    sequences = SequenceFactory.from_directory(test_dir)
    sequence = sequences[0]

    # Test for TRUE - all files exist
    assert sequence.exists == SequenceExistence.TRUE

    # Delete one file to test PARTIAL
    (test_dir / "file.0003.exr").unlink()
    assert sequence.exists == SequenceExistence.PARTIAL

    # Delete remaining files to test FALSE
    for file in files:
        path = test_dir / file
        if path.exists():
            path.unlink()

    assert sequence.exists == SequenceExistence.FALSE

    # Cleanup
    shutil.rmtree(test_dir)
