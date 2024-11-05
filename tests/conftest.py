import pytest
from pathlib import Path
import yaml


@pytest.fixture
def load_test_cases():
    """Loads test cases from YAML files."""
    def _load_from_yaml(filename):
        test_cases_dir = Path(__file__).parent / 'test_cases'
        yaml_path = test_cases_dir / filename
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f)
    return _load_from_yaml


@pytest.fixture
def create_Item_test_files(tmp_path, load_test_cases):
    """Creates test files based on YAML test cases For testing Item in
    isolation."""
    def _create_files(yaml_filename):

        cases = load_test_cases(yaml_filename)
        test_dir = tmp_path / "test_sequence"
        test_dir.mkdir()

        for case in cases:

            case['test_dir'] = test_dir
            relative_path = Path(case['data']['path'].lstrip('/'))
            path = test_dir / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            case['real_file'] = path

        return cases

    return _create_files

@pytest.fixture
def create_files_from_list(tmp_path):
    """Creates temporary files from a list and returns their Path objects."""
    test_dir = tmp_path / "test_files"
    test_dir.mkdir()
    
    def _create_files(file_list):
        paths = []
        for file in file_list:
            path = test_dir / file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            paths.append(path)
        return paths
    
    return _create_files


@pytest.fixture
def create_FileSequence_test_files(tmp_path, load_test_cases):
    """Creates test files based on YAML test cases For testing FileSequence in
    isolation."""
    def _create_files(yaml_filename):

        cases = load_test_cases(yaml_filename)
        test_dir = tmp_path / "test_sequence"
        test_dir.mkdir()

        for case in cases:

            case['test_dir'] = test_dir
            case['real_files'] = []
            relative_path = Path(case['data']['path'].lstrip('/'))
            path = test_dir / relative_path
            path.mkdir(parents=True, exist_ok=True)
            files = case['data']['files']
            for file in files:
                
                full_path = path / file
                full_path.touch()
                case['real_files'].append(path)

            return cases

    return _create_files
