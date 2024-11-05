from pysequitur.file_sequence import FileSequence, Parser
from pathlib import Path
import pytest

def test_suffix_parsing():
    
    files = [
        'frame.0001_a.png',
        'frame.0002_a.png',
        'frame.0003_a.png',
        'frame.0004_a.png',
        'frame.0005_a.png',
        'frame.0001_b.png',
        'frame.0002_b.png',
        'frame.0003_b.png',
        'frame.0004_b.png',
        'frame.0005_b.png',
    ]

    sequences = Parser.from_file_list(files)

    assert len(sequences) == 2