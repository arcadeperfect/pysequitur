import pytest
from pathlib import Path
import yaml


@pytest.fixture
def load_test_cases():
    """Loads test cases from YAML files"""
    def _load_from_yaml(filename):
        test_cases_dir = Path(__file__).parent / 'test_cases'
        yaml_path = test_cases_dir / filename
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f)
    return _load_from_yaml


@pytest.fixture
def create_Item_test_files(tmp_path, load_test_cases):
    """Creates test files based on YAML test cases"""
    def _create_files(yaml_filename):
        # Load the test cases
        cases = load_test_cases(yaml_filename)

        # Create test directory
        test_dir = tmp_path / "test_sequence"
        test_dir.mkdir()
        # real_files = []
        for case in cases:

            case['test_dir'] = test_dir

            relative_path = Path(case['data']['path'].lstrip('/'))

            path = test_dir / relative_path
            
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            case['real_file'] = path
        
            # path = test_dir / case['data']['path']
            # print(path)
            # path.touch()
            # real_files.append(path)

        return cases
    
    return _create_files