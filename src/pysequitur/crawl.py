from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


from .file_sequence import FileSequence, SequenceParser
from .file_types import MOVIE_FILE_TYPES

# MOVIE_FILE_TYPES = {
#     "webm",
#     "mkv",
#     "flv",
#     "vob",
#     "ogv",
#     "ogg",
#     "rrc",
#     "gifv",
#     "mng",
#     "mov",
#     "avi",
#     "qt",
#     "wmv",
#     "yuv",
#     "rm",
#     "asf",
#     "amv",
#     "mp4",
#     "m4p",
#     "m4v",
#     "mpg",
#     "mp2",
#     "mpeg",
#     "mpe",
#     "mpv",
#     "m4v",
#     "svi",
#     "3gp",
#     "3g2",
#     "mxf",
#     "roq",
#     "nsv",
#     "flv",
#     "f4v",
#     "f4p",
#     "f4a",
#     "f4b",
#     "mod",
# }

DEFAULT_ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "dpx",
    "exr",
    "mov",
    "mp4",
    "png",
    "tif",
    "tiff",
}


@dataclass
class Results:
    dir: Path
    sequences: List[FileSequence]
    movs: List[Path]
    rogues: List[Path]
    depth: int


class Node:
    def __init__(
        self,
        path: Path,
        allowed_extensions: set[str] = DEFAULT_ALLOWED_EXTENSIONS,
        max_depth: Optional[int] = None,
        current_depth: int = 0,
    ):
        self.path: Path = path

        normalized_extensions = {ext.lower().lstrip(".") for ext in allowed_extensions}
        allowed_movie_exts = normalized_extensions.intersection(MOVIE_FILE_TYPES)
        allowed_sequence_exts = normalized_extensions.difference(MOVIE_FILE_TYPES)

        self.movies: set[Path] = set()
        self.dirs: list[Path] = []

        sequence_candidates: list[str] = []

        try:
            for item in path.iterdir():
                if item.is_dir():
                    self.dirs.append(item)
                elif item.is_file():
                    if item.name[0] == ".":
                        continue
                    ext = item.suffix.lower().lstrip(".")
                    if ext in allowed_movie_exts:
                        self.movies.add(item)
                    elif ext in allowed_sequence_exts:
                        sequence_candidates.append(item.name)
        except (PermissionError, OSError) as e:
            print(f"Error accessing {path}: {e}")

        # Only process sequences if we found candidate files
        if sequence_candidates:
            results: SequenceParser.ParseResult = SequenceParser.from_file_list(
                sequence_candidates, 1, path, allowed_sequence_exts
            )
            self.sequences: list[FileSequence] = results.sequences
            self.rogues: list[Path] = results.rogues
        else:
            self.sequences = []
            self.rogues = []

        # Process subdirectories with depth control
        if max_depth is None or current_depth < max_depth:
            self.nodes: list[Node] = [
                Node(d, allowed_extensions, max_depth, current_depth + 1)
                for d in self.dirs
            ]
        else:
            self.nodes: list[Node] = []


def recursive_scan(path: Path, max_depth: Optional[int] = None) -> Node:
    return Node(path, max_depth=max_depth)


def visualize_tree(
    node: Node, prefix="", is_last=True, max_level=None, level=0, counts=None
):
    """
    Visualize the directory tree with sequences, movies, and rogues in a tree-like format.
    Similar to the 'tree' command output.

    Args:
        node: The node to visualize
        prefix: The prefix string for the current line
        is_last: Whether this node is the last in its parent's children
        max_level: Maximum depth to visualize (None for unlimited)
        level: Current depth level
        counts: Dictionary to track counts of different item types
    """

    if counts is None:
        counts = {"dirs": 0, "sequences": 0, "movies": 0, "rogues": 0}
        is_root = True
    else:
        is_root = False

    if max_level is not None and level > max_level:
        print(prefix + ("└── " if is_last else "├── ") + "...")
        return counts

    if level > 0:  # Don't count the root
        counts["dirs"] += 1

    if level == 0:
        print(node.path)
    else:
        print(prefix + ("└── " if is_last else "├── ") + node.path.name + "/")

    new_prefix = prefix + ("    " if is_last else "│   ")

    dirs_count = len(node.nodes)
    for i, subnode in enumerate(node.nodes):
        is_last_dir = i == dirs_count - 1
        is_last_item = is_last_dir and not (
            node.sequences or node.movies or node.rogues
        )
        visualize_tree(subnode, new_prefix, is_last_item, max_level, level + 1, counts)

    counts["sequences"] += len(node.sequences)
    counts["movies"] += len(node.movies)
    counts["rogues"] += len(node.rogues)

    file_items = []

    for seq in node.sequences:
        file_items.append((f"[SEQ] {seq}", "sequence"))

    for movie in sorted(node.movies):
        file_items.append((f"[MOV] {movie.name}", "movie"))

    for rogue in node.rogues:
        file_items.append((f"[ROG] {rogue}", "rogue"))

    for i, (item, item_type) in enumerate(file_items):
        is_last_file = i == len(file_items) - 1
        print(new_prefix + ("└── " if is_last_file else "├── ") + item)

    if is_root:
        total_files = counts["sequences"] + counts["movies"] + counts["rogues"]
        print(f"\n{counts['dirs']} directories, {total_files} files")
        print(
            f"  {counts['sequences']} sequences, {counts['movies']} movies, {counts['rogues']} rogues"
        )

    return counts


def traverse_nodes(node: Node, depth: int = 0) -> List[Results]:
    """
    Traverse all nodes in the tree and return a flat list of Results objects.

    Args:
        node: The node to start traversal from
        depth: Current depth in the tree

    Returns:
        List of Results objects for each node
    """
    results = []

    # Create Results object for current node
    # Convert rogues from strings to Path objects
    rogues_as_paths = [node.path / rogue for rogue in node.rogues]

    current_result = Results(
        dir=node.path,
        sequences=node.sequences,
        movs=list(node.movies),  # Convert set to list
        rogues=rogues_as_paths,
        depth=depth,
    )

    # Add to results list
    results.append(current_result)

    # Recursively process child nodes
    for child_node in node.nodes:
        child_results = traverse_nodes(child_node, depth + 1)
        results.extend(child_results)

    return results
