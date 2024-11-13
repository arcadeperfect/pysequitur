import pytest
from pathlib import Path
import yaml

@pytest.fixture
def parse_yaml():
    def _parse_yaml(yaml_file):
        # data_dir = Path(__file__).parent / 'test_data'
        # yaml_file = data_dir / yaml_file
        with open(yaml_file) as f:
            return yaml.safe_load(f)
    return _parse_yaml

@pytest.fixture
def generate_files(tmp_path):  # Added tmp_path parameter
    """
    accepts a list of file names and generates empty files in a test directory
    """

    created_files = []
    test_dir = tmp_path / "test_sequence"
    test_dir.mkdir()
    
    def _generate_files(file_paths: list[Path]):
        for path in file_paths:
            # Strip leading / and create relative to test_dir
            relative_path = Path(str(path).lstrip('/'))
            full_path = test_dir / relative_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()
            created_files.append(full_path)
        return created_files
    
    yield _generate_files
    
@pytest.fixture
def parse_item_yaml(parse_yaml, generate_files, tmp_path):
    """
    parses a yaml with a list of items and associated expected item parse results
    """
    
    def _parse_item_yaml(yaml_file):
        test_env = parse_yaml(yaml_file)
        paths = [Path(case['data']['path']) for case in test_env]
        created_files = generate_files(paths)
        
        # Add the real file paths back to the test cases
        for case, real_file in zip(test_env, created_files):
            case['real_file'] = real_file
            case['tmp_dir'] = tmp_path
        
        return test_env
    return _parse_item_yaml
    
@pytest.fixture
def parse_sequence_yaml(parse_yaml, generate_files, tmp_path):
    """
    parses a yaml with a list of sequences and associated expected sequence parse results
    """
    
    
    def _parse_sequence_yaml(yaml_file):
        test_env = parse_yaml(yaml_file)
        
        for case in test_env:
            paths = []
            path = case['path']
            for file in case['files']:
                paths.append(Path(path) / file)
                
            created_files = generate_files(paths)
            case['real_files'] = created_files
            case['tmp_dir'] = tmp_path / "test_sequence"
        
        return test_env
    return _parse_sequence_yaml
    
@pytest.fixture
def parse_jumble_yaml(parse_yaml, generate_files, tmp_path):
    """
    parses a yaml with a single list continging multiple sequences and an int representing expected number of sequences parsed
    """
    def _parse_jumble_yaml(yaml_file):
        print(yaml_file)
        if not Path(yaml_file).exists():
            raise FileNotFoundError(f"File {yaml_file} not found")
        test_env = parse_yaml(yaml_file)
        if(len(test_env['files']) == 0):
            raise ValueError("No files found in the yaml")
        paths = [Path(t) for t in test_env['files']]
        created_files = generate_files(paths)
        test_env['real_files'] = created_files
        test_env['tmp_dir'] = tmp_path / "test_sequence"
        return test_env
    
    return _parse_jumble_yaml