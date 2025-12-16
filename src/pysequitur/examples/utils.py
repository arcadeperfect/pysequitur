import os
from pathlib import Path

from pysequitur import Components


def create_some_sequences():
    components_1 = Components(
        prefix="render",
        delimiter="_",
        padding=3,
        suffix="_final",
        extension="exr",
    )

    components_2 = Components(
        prefix="plate",
        delimiter=".",
        padding=5,
        extension="dpx",
    )

    components_3 = Components(
        prefix="shot",
        delimiter="-",
        padding=4,
        extension="exr",
    )

    directory = os.path.dirname(os.path.abspath(__file__)) + "/files"

    generate_file_sequence(components_1, 1, 10, directory)
    generate_file_sequence(components_2, 1001, 1010, directory)
    generate_file_sequence(components_3, 100, 110, directory)

    return directory


def generate_file_sequence(
    components: Components, first_frame: int, last_frame: int, directory: str
) -> None:
    padding = components.padding or len(str(last_frame))
    padding = max(len(str(last_frame)), padding)

    suffix = components.suffix or ""

    for frame_number in range(first_frame, last_frame + 1):
        this_frame = f"{components.prefix}{components.delimiter}{str(frame_number).zfill(padding)}{suffix}.{components.extension}"
        p = Path(Path(directory) / this_frame)
        p.touch()
