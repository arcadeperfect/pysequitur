from pysequitur import Components, FileSequence
from pysequitur.examples.utils import create_some_sequences
import os


def run_examples():

    # generate some empty files
    temp_files_directory = create_some_sequences()

    print("\n\nGenerated these files:\n")

    for file in sorted(os.listdir(temp_files_directory)):
        print(file)

    
    ## Parse a directory of files

    parsed_sequences = FileSequence.from_directory(temp_files_directory)

    print("\n\nFound sequences:\n")
    for seq in parsed_sequences:
        print(seq)


    ## Parse by components:

    sequences = FileSequence.from_components_in_directory(Components(prefix="render"), temp_files_directory)

    print("\n\nParser found one sequence with prefix 'render':\n")
    for seq in sequences:
        print(seq)

    sequences = FileSequence.from_components_in_directory(Components(extension="exr"), temp_files_directory)

    print("\n\nParser found two sequence with extension 'exr':\n")
    for seq in sequences:
        print(seq)

    sequences = FileSequence.from_components_in_directory(Components(prefix="render", extension="exr"), temp_files_directory)

    print("\n\nParser found one sequence with prefix 'render' and extension 'exr':\n")
    for seq in sequences:
        print(seq)


    ## Parse by filename

    seq = FileSequence.from_sequence_filename_in_directory("render_###_final.exr", temp_files_directory)

    print("\n\nParsed a single sequence:\n")
    print(seq)



    ## Operations:

    seq = FileSequence.from_sequence_filename_in_directory("render_###_final.exr", temp_files_directory)

    seq.move("/new/directory")
    seq.rename("new_name")
    seq.offset_frames(100)  # Shift all frame numbers by 100
    new_sequence = seq.copy("/new/directory")

    print("\n\nRenamed sequence:\n")
    print(new_sequence)
