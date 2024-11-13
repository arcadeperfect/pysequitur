import pytest
from pathlib import Path
import yaml

@pytest.fixture
def yaml_to_dict():
    def _yaml_to_dict(yaml_file):
        # data_dir = Path(__file__).parent / 'test_data'
        # yaml_file = data_dir / yaml_file
        with open(yaml_file) as f:
            return yaml.safe_load(f)
    return _yaml_to_dict

@pytest.fixture
def generate_files(tmp_path):  # Added tmp_path parameter
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
def parse_item_yaml(yaml_to_dict, generate_files, tmp_path):
    def _parse_item_yaml(yaml_file):
        test_env = yaml_to_dict(yaml_file)
        paths = [Path(case['data']['path']) for case in test_env]
        created_files = generate_files(paths)
        
        # Add the real file paths back to the test cases
        for case, real_file in zip(test_env, created_files):
            case['real_file'] = real_file
            case['tmp_dir'] = tmp_path
        
        return test_env
    return _parse_item_yaml