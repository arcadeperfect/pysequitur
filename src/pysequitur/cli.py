"""Command-line tool for listing parsed file sequences (``lsq``).

Works like ``ls`` but collapses frame-based file sequences into a single
entry showing the sequence pattern, frame range and gaps. Uses only the
standard library.
"""

import argparse
import sys
from pathlib import Path

from pysequitur import FileSequence, SequenceFactory


def _format_ranges(numbers: list[int]) -> str:
    """Collapse a sorted int list into compact range notation: '1-3,7,9-10'."""
    if not numbers:
        return ""
    parts: list[str] = []
    start = prev = numbers[0]
    for n in numbers[1:]:
        if n == prev + 1:
            prev = n
            continue
        parts.append(str(start) if start == prev else f"{start}-{prev}")
        start = prev = n
    parts.append(str(start) if start == prev else f"{start}-{prev}")
    return ",".join(parts)


def _format_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def _sequence_size(seq: FileSequence) -> int:
    total = 0
    for item in seq.items:
        try:
            total += item.path.stat().st_size
        except OSError:
            pass
    return total


def _sequence_filenames(seq: FileSequence) -> set[str]:
    return {item.filename for item in seq.items}


def _long_detail(seq: FileSequence) -> str:
    rng = f"{seq.first_frame}-{seq.last_frame}"
    count = f"{seq.actual_frame_count}/{seq.frame_count}"
    detail = f"{rng:>14}  {count:>10} frames  pad {seq.padding}"
    missing = seq.missing_frames
    if missing:
        detail += f"  missing [{_format_ranges(missing)}]"
    return detail + f"  {_format_size(_sequence_size(seq)):>9}"


def _loose_files(directory: Path, sequences: list[FileSequence]) -> list[str]:
    covered: set[str] = set()
    for seq in sequences:
        covered |= _sequence_filenames(seq)
    return sorted(
        p.name for p in directory.iterdir() if p.is_file() and p.name not in covered
    )


def _list_directory(directory: Path, args: argparse.Namespace) -> int:
    if not directory.is_dir():
        print(f"lsq: {directory}: not a directory", file=sys.stderr)
        return 1

    sequences = SequenceFactory.from_directory(directory, min_frames=args.min_frames)
    sequences.sort(key=lambda s: s.sequence_string)

    rows: list[tuple[str, str]] = []
    for seq in sequences:
        if args.long:
            rows.append((seq.sequence_string, _long_detail(seq)))
        else:
            rng = f"{seq.first_frame}-{seq.last_frame}"
            rows.append(
                (seq.sequence_string, f"{rng}  ({seq.actual_frame_count} frames)")
            )

    width = max((len(p) for p, _ in rows), default=0)
    for pattern, detail in rows:
        print(f"{pattern.ljust(width)}  {detail}")

    if args.all:
        loose = _loose_files(directory, sequences)
        if loose:
            if rows:
                print()
            print("\n".join(loose))

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="lsq",
        description="List parsed file sequences in a directory, like ls.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="directories to list (default: current directory)",
    )
    parser.add_argument(
        "-l",
        "--long",
        action="store_true",
        help="long format: frame counts, gaps, padding and total size",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="also list files that are not part of any sequence",
    )
    parser.add_argument(
        "-m",
        "--min-frames",
        type=int,
        default=2,
        help="minimum frames for a group to count as a sequence (default: 2)",
    )
    args = parser.parse_args(argv)

    paths = [Path(p) for p in args.paths]
    exit_code = 0
    for i, directory in enumerate(paths):
        if len(paths) > 1:
            if i:
                print()
            print(f"{directory}:")
        exit_code |= _list_directory(directory, args)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
