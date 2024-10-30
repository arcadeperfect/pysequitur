# from pathlib import Path
# from pysequitur.file_sequence import FileSequence, Parser

# def test_FileSequence(create_FileSequence_test_files):
#     test_cases_dir = Path(__file__).parent / 'FileSequence_test_cases'
#     yaml_file = test_cases_dir / '1.yaml'

#     test_env = create_FileSequence_test_files(yaml_file)

#     # print("testing")

#     for test in test_env:

#         data = test['data']
#         files = data['files']


#         items = [Parser.parse_filename(i, test['test_dir']) for i in files]

#         fileSequence = FileSequence(items)

        