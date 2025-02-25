import re

# from typing import List, Optional, Tuple, Union


def extract_shot_from_single_path(file_path: str) -> tuple[str, str]:
    """
    Extract shot number from a single file path, being careful to distinguish from version numbers.

    Args:
        file_path: Absolute or relative path to a file or image sequence

    Returns:
        Tuple of (padded shot number, original path)
    """
    # Convert backslashes to forward slashes for consistency
    file_path = file_path.replace("\\", "/")

    # Common patterns for shot numbers, avoiding version numbers
    patterns = [
        r"(?:^|/)(?:shot|sq|sequence)[-_]?(\d+)",  # shot_020, sequence_020
        r"(?:^|/)s(\d+)",  # s020
        r"(?:^|/)(\d+)(?:_[^v]|/)",  # 020_comp, 020/
    ]

    for pattern in patterns:
        match = re.search(pattern, file_path, re.IGNORECASE)
        if match:
            shot_num = match.group(1)
            # Pad to at least 3 digits
            return shot_num.zfill(3), file_path

    # If no clear shot number found, look for any number not preceded by 'v'
    numbers = re.findall(r"(?<!v)\d+", file_path)
    if numbers:
        # Take the first number that's not clearly a version
        return numbers[0].zfill(3), file_path

    # If no shot number found, return placeholder
    return "000", file_path


def extract_shots_from_project_paths(file_paths: list[str]) -> list[tuple[str, str]]:
    """
    Extract shot numbers from a list of paths known to be from the same project.
    Uses common path segments to improve accuracy.

    Args:
        file_paths: List of paths from the same project

    Returns:
        List of tuples (padded shot number, original path)
    """
    if not file_paths:
        return []

    # Find common path structure
    path_parts = [path.replace("\\", "/").split("/") for path in file_paths]
    min_length = min(len(parts) for parts in path_parts)

    # Find positions where numbers commonly appear
    number_positions = []
    for i in range(min_length):
        numbers_at_pos = []
        for parts in path_parts:
            if re.search(r"\d+", parts[i]):
                numbers_at_pos.append(parts[i])
        if numbers_at_pos:
            number_positions.append((i, len(numbers_at_pos)))

    # Sort by frequency of number occurrence
    number_positions.sort(key=lambda x: x[1], reverse=True)

    results = []
    for path in file_paths:
        parts = path.replace("\\", "/").split("/")
        shot_num = None

        # First try positions where numbers commonly appear
        for pos, _ in number_positions:
            if pos < len(parts):
                numbers = re.findall(r"(?<!v)\d+", parts[pos])
                if numbers:
                    shot_num = numbers[0]
                    break

        # If no shot number found, fall back to single path method
        if not shot_num:
            shot_num, _ = extract_shot_from_single_path(path)

        results.append((shot_num.zfill(3), path))

    return results


def extract_shots_from_mixed_paths(file_paths: list[str]) -> list[tuple[str, str]]:
    """
    Extract shot numbers from a list of paths that may be from different projects.
    Groups similar paths together and applies the most appropriate extraction method.

    Args:
        file_paths: List of paths that may be from different projects

    Returns:
        List of tuples (padded shot number, original path)
    """
    if not file_paths:
        return []

    # Group paths by common structure
    def get_path_signature(path: str) -> str:
        # Create a signature based on the path structure
        parts = path.replace("\\", "/").split("/")
        return "_".join(str(bool(re.search(r"\d+", part))) for part in parts)

    # Group paths by signature
    path_groups = {}
    for path in file_paths:
        sig = get_path_signature(path)
        path_groups.setdefault(sig, []).append(path)

    results = []
    for group in path_groups.values():
        if len(group) > 1:
            # Use project paths method for groups
            results.extend(extract_shots_from_project_paths(group))
        else:
            # Use single path method for unique structures
            results.extend([extract_shot_from_single_path(path) for path in group])

    # Sort by shot number, then by original path
    results.sort(key=lambda x: (x[0], x[1]))

    return results


# Example usage:
if __name__ == "__main__":
    # Single path examples
    test_paths = [
        "/path/to/images/shot_020/render_020_main_v123.mov",
        "/path/to/images/shot_020/render_020_main_v123.####.exr",
        "/shows/project/sq_015/comp/v002/",
        "/shows/project/s010/lighting/",
    ]

    print("\nTesting single path extraction:")
    for path in test_paths:
        shot_num, original = extract_shot_from_single_path(path)
        print(f"Path: {path}")
        print(f"Shot: {shot_num}")

    print("\nTesting project paths extraction:")
    project_results = extract_shots_from_project_paths(test_paths)
    for shot_num, path in project_results:
        print(f"Shot: {shot_num} - Path: {path}")

    # Mixed paths example
    mixed_paths = test_paths + [
        "/different/project/sequence_030/final/",
        "/another/show/shot_040/comp_v001.mov",
    ]

    print("\nTesting mixed paths extraction:")
    mixed_results = extract_shots_from_mixed_paths(mixed_paths)
    for shot_num, path in mixed_results:
        print(f"Shot: {shot_num} - Path: {path}")
