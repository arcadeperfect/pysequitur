from pathlib import Path
from typing import List, Optional

from pysequitur import FileSequence, SequenceParser

MOVIE_FILE_TYPES = {
    "webm",
    "mkv",
    "flv",
    "vob",
    "ogv",
    "ogg",
    "rrc",
    "gif",
    "vmn",
    "gmov",
    "avi",
    "qtw",
    "mv",
    "yuv",
    "rma",
    "sfa",
    "mp4",
    "m4p",
    "m4v",
    "mpg",
    "mp2",
    "mpeg",
    "mpe",
    "mpv",
    "svi",
    "3gp",
    "3g2",
    "mxf",
    "roq",
    "nsv",
    "f4v",
    "f4p",
    "f4a",
    "f4b",
    "mod",
}


class Node:
    def __init__(self, path: Path, allowed_extensions: set[str]):
        self.path = path

        allowed_extensions = {ext.lower().lstrip(".") for ext in allowed_extensions}

        allowed_movies = {ext for ext in allowed_extensions if ext in MOVIE_FILE_TYPES}

        allowed_extensions = {
            ext for ext in allowed_extensions if ext not in MOVIE_FILE_TYPES
        }

        results = SequenceParser.from_directory(path, 1, allowed_extensions)
        self.sequences = results.sequences
        self.rogues = results.rogues
        self.movies = {
            file
            for file in set(path.iterdir())
            if file.suffix.lower().lstrip(".") in allowed_movies
        }

        # self.sequences = FileSequence.find_sequences_in_path(path)
        self.dirs = [d for d in path.iterdir() if d.is_dir()]

        self.nodes = [Node(d, allowed_extensions) for d in self.dirs]


def visualize_tree(node: Node, level=0):
    print("\t" * level + str(node.path))
    for s in node.sequences:
        print("\t" * (level) + str(s.sequence_string))

    for n in node.nodes:
        visualize_tree(n, level + 1)


def collect_sequences(node: Node) -> list[FileSequence]:
    sequences = []
    sequences.extend(node.sequences)
    for n in node.nodes:
        sequences.extend(collect_sequences(n))
    return sequences
