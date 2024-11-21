from pysequitur.file_sequence import FileSequence
from pathlib import Path

def test_sequence_string():
    # Create test directory and files
    test_dir = Path("test_sequence")
    test_dir.mkdir(exist_ok=True)
    
    # Test cases with different patterns
    test_cases = [
        {
            "files": ["render.0001.exr", "render.0002.exr"],
            "expected": "render.####.exr"
        },
        {
            "files": ["shot_001_v1.exr", "shot_002_v1.exr"],
            "expected": "shot_###_v1.exr"
        },
        {
            "files": ["comp-0001-preview.exr", "comp-0002-preview.exr"],
            "expected": "comp-####-preview.exr"
        },
        {
            "files": ["anim.00001.beauty.exr", "anim.00002.beauty.exr"],
            "expected": "anim.#####.beauty.exr"
        }
    ]
    
    for case in test_cases:
        # Create files
        for file in case["files"]:
            (test_dir / file).touch()
            
        # Get sequence
        sequences = FileSequence.find_sequences_in_path(test_dir)
        sequence = sequences[0]
        
        # Test sequence string
        assert sequence.sequence_string == case["expected"]
        
        # # Cleanup files
        # for file in case["files"]:
        #     (test_dir / file).unlink()
            
    # Clean up directory
    # test_dir.rmdir()