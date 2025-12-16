import os
from pathlib import Path

from pysequitur import Components, SequenceFactory
from pysequitur.examples.utils import create_some_sequences


def run_examples():
    # generate some empty files
    temp_files_directory = Path(create_some_sequences())

    print("\n\nGenerated these files:\n")

    for file in sorted(os.listdir(temp_files_directory)):
        print(file)

    ## Parse a directory of files

    parsed_sequences = SequenceFactory.from_directory(temp_files_directory)

    print("\n\nFound sequences:\n")
    for seq in parsed_sequences:
        print(seq)

    ## Parse by components:

    sequences = SequenceFactory.from_directory_with_components(
        Components(prefix="render"), temp_files_directory
    )

    print("\n\nParser found one sequence with prefix 'render':\n")
    for seq in sequences:
        print(seq)

    sequences = SequenceFactory.from_directory_with_components(
        Components(extension="exr"), temp_files_directory
    )

    print("\n\nParser found two sequences with extension 'exr':\n")
    for seq in sequences:
        print(seq)

    sequences = SequenceFactory.from_directory_with_components(
        Components(prefix="render", extension="exr"), temp_files_directory
    )

    print("\n\nParser found one sequence with prefix 'render' and extension 'exr':\n")
    for seq in sequences:
        print(seq)

    ## Parse by sequence string

    seq = SequenceFactory.from_directory_with_sequence_string(
        "render_###_final.exr", temp_files_directory
    )

    print("\n\nParsed a single sequence:\n")
    print(seq)

    ## Operations (preview without executing):

    seq = SequenceFactory.from_directory_with_sequence_string(
        "render_###_final.exr", temp_files_directory
    )

    # All operations return SequenceResult with (sequence, plan)
    # You can preview the plan before executing:

    result = seq.rename(Components(prefix="new_name"))
    print("\n\nRename plan (not executed yet):\n")
    print(result.plan)

    # To execute, call .apply() or result.plan.execute()
    # new_seq = result.apply()

    # You can also chain with tuple unpacking:
    new_seq, plan = seq.offset_frames(100)
    print("\n\nOffset frames plan:\n")
    print(plan)

    # Move operation
    new_seq, plan = seq.move(Path("/new/directory"))
    print("\n\nMove plan:\n")
    print(plan)

    # Copy operation
    new_seq, plan = seq.copy(new_directory=Path("/new/directory"))
    print("\n\nCopy plan:\n")
    print(plan)

    print("\n\nNew sequence (after hypothetical operations):\n")
    print(new_seq)


if __name__ == "__main__":
    run_examples()
