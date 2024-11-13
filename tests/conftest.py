import pytest
from pathlib import Path
import yaml

@pytest.fixture
def test_data_dir():
    return Path(__file__).parent / 'test_data'

@pytest.fixture
def parse_yaml():
    def _parse_yaml(yaml_file):
        with open(yaml_file) as f:
            return yaml.safe_load(f)
    return _parse_yaml

@pytest.fixture
def generate_files(tmp_path):
    """
    Accepts a list of file names and generates empty files in a test directory.
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
            print(full_path)
            full_path.touch()
            assert full_path.exists()
            created_files.append(full_path)
        return created_files

    return _generate_files

@pytest.fixture
def parse_item_yaml(parse_yaml, generate_files, tmp_path, test_data_dir):
    """
    Parses all YAML files in the test_data directory and returns a list of test environments.
    """
    def _parse_item_yaml():
        test_env_list = []
        yaml_files = test_data_dir.glob('item_*.yaml')
        for yaml_file in yaml_files:
            test_env = parse_yaml(yaml_file)
            # for case in test_env:
            #     print(case['data']['path'])
            paths = [Path(case['data']['path']) for case in test_env]
            # print(paths)
            created_files = generate_files(paths)

            # Add the real file paths back to the test cases
            for case, real_file in zip(test_env, created_files):
                case['real_file'] = real_file
                case['tmp_dir'] = tmp_path / "test_sequence"

            test_env_list.extend(test_env)
        return test_env_list
    return _parse_item_yaml

@pytest.fixture
def parse_sequence_yaml(parse_yaml, generate_files, tmp_path, test_data_dir):
    def _parse_sequence_yaml():
        test_env_list = []
        yaml_files = test_data_dir.glob('sequences_*.yaml')
        
        for yaml_file in yaml_files:
            test_env = parse_yaml(yaml_file)
            for case in test_env:
                # Create the files for this case
                these_paths = [Path(case['path']) / file for file in case['files']]
                # print(these_paths)
                real_files = generate_files(these_paths)
                
                # Add additional data to the test case
                case['real_files'] = real_files
                case['tmp_dir'] = tmp_path / "test_sequence"
                
            test_env_list.extend(test_env)
            
        return test_env_list
    return _parse_sequence_yaml