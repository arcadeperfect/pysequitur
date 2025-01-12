# from dataclasses import dataclass
from pathlib import Path
from typing import List

from pysequitur import FileSequence

# @dataclass
# class Node:

#     path: Path
#     sequences: List[FileSequence]
#     # loose_files: List[Path]
#     sub_nodes: List['Node']


# def crawl(path: Path, allowed_file_types: List[str]) -> Node:

#     seqs = FileSequence.find_sequences_in_path(path)
#     dirs = [f for f in path.iterdir() if f.is_dir()]


#     return Node(path, seqs, loose_files, sub_nodes)


class Node:
    def __init__(self, path: Path):
        self.path = path

        self.sequences = FileSequence.find_sequences_in_path(path)
        self.dirs = [d for d in path.iterdir() if d.is_dir()]

        self.nodes = [Node(d) for d in self.dirs]


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
